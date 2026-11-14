from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from datetime import UTC, datetime
from html import unescape
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from .models import (
    Candidate,
    CandidateValidation,
    ContactValidationRecord,
    FieldValidationRecord,
)

SOURCE_VALIDATION_TIMEOUT_SECONDS = 10.0
MAX_SOURCE_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_SOURCE_REDIRECT_HOPS = 5
_REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})
_ALLOWED_SCHEMES = frozenset({"http", "https"})
_FORBIDDEN_HOST_SUFFIXES = (".localhost", ".local", ".internal")
_CGNAT_NETWORK = ipaddress.ip_network("100.64.0.0/10")
_IPV6_ULA_NETWORK = ipaddress.ip_network("fc00::/7")
_FLY_INTERNAL_NETWORK = ipaddress.ip_network("fdaa::/16")
_SUPPORTED_SOURCE_FIELD_STATUSES = {"supported", "verified_found"}

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_K12_TECH_TITLE_MARKERS = (
    "technology",
    "information technology",
    "information services",
    "cio",
    "cto",
    "network",
    "infrastructure",
    "cybersecurity",
)
_K12_TECH_ROLE_PATTERNS = (
    re.compile(r"\bchief\s+technology\s+officer\b", re.IGNORECASE),
    re.compile(r"\bchief\s+information\s+officer\b", re.IGNORECASE),
    re.compile(r"\bCIO\b", re.IGNORECASE),
    re.compile(r"\bCTO\b", re.IGNORECASE),
    re.compile(r"\bdirector\s+of\s+(?:information\s+)?technology\b", re.IGNORECASE),
    re.compile(r"\binformation\s+technology\s+\(IT\)\s+director\b", re.IGNORECASE),
    re.compile(r"\binformation\s+technology\s+director\b", re.IGNORECASE),
    re.compile(r"\btechnology\s+services\b", re.IGNORECASE),
    re.compile(r"\btech(?:nology)?\s+infrastructure\s+and\s+cybersecurity\b", re.IGNORECASE),
    re.compile(r"\bnetwork\s+(?:administrator|manager|director)\b", re.IGNORECASE),
)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _normalize_source_text(text: str) -> str:
    cleaned = _HTML_TAG_RE.sub(" ", unescape(text))
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


def _phrase_pattern(value: str) -> re.Pattern[str]:
    parts = [re.escape(part) for part in value.strip().split() if part]
    if not parts:
        return re.compile(r"(?!x)x")
    return re.compile(r"\s+".join(parts), re.IGNORECASE)


def _find_evidence_snippet(source_text: str, field_value: str, window: int = 80) -> str | None:
    match = _phrase_pattern(field_value).search(source_text)
    if not match:
        return None

    start = max(0, match.start() - window)
    end = min(len(source_text), match.end() + window)
    snippet = source_text[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(source_text):
        snippet = f"{snippet}..."
    return snippet


def _snippet_from_span(source_text: str, start: int, end: int, window: int = 120) -> str:
    snippet_start = max(0, start - window)
    snippet_end = min(len(source_text), end + window)
    snippet = source_text[snippet_start:snippet_end].strip()
    if snippet_start > 0:
        snippet = f"...{snippet}"
    if snippet_end < len(source_text):
        snippet = f"{snippet}..."
    return snippet


def _find_title_role_evidence_snippet(
    source_text: str,
    field_value: str,
    *,
    context_values: tuple[str, ...] = (),
) -> str | None:
    lowered_title = field_value.lower()
    if not any(marker in lowered_title for marker in _K12_TECH_TITLE_MARKERS):
        return None

    role_matches = [
        match
        for pattern in _K12_TECH_ROLE_PATTERNS
        for match in pattern.finditer(source_text)
    ]
    if not role_matches:
        return None

    context_matches = [
        match
        for context in context_values
        if _has_text(context)
        for match in [_phrase_pattern(context).search(source_text)]
        if match is not None
    ]
    for context_match in context_matches:
        for role_match in role_matches:
            span_start = min(context_match.start(), role_match.start())
            span_end = max(context_match.end(), role_match.end())
            if span_end - span_start <= 280:
                return _snippet_from_span(source_text, span_start, span_end)

    role_match = role_matches[0]
    return _snippet_from_span(source_text, role_match.start(), role_match.end())


def _field_record_for_missing_source(
    field_name: str,
    field_value: Any,
    *,
    checked_at: str,
) -> FieldValidationRecord:
    if _has_text(field_value):
        return FieldValidationRecord(
            status="failed",
            source_url=None,
            checked_at=checked_at,
            notes=f"Could not validate {field_name} because source_url was not provided.",
        )

    return FieldValidationRecord(
        status="missing",
        source_url=None,
        checked_at=checked_at,
        notes=f"{field_name} is not present on the candidate.",
    )


def _contact_record_for_missing_source(
    field_name: str,
    field_value: Any,
    *,
    checked_at: str,
) -> ContactValidationRecord:
    if _has_text(field_value):
        return ContactValidationRecord(
            status="failed",
            source_url=None,
            checked_at=checked_at,
            notes=f"Could not validate {field_name} because source_url was not provided.",
        )

    return ContactValidationRecord(
        status="missing",
        source_url=None,
        checked_at=checked_at,
        notes=f"{field_name} is not present on the candidate.",
    )


def _field_record_for_access_failure(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    note: str,
) -> FieldValidationRecord:
    if _has_text(field_value):
        status = "failed"
        field_note = note
    else:
        status = "missing"
        field_note = f"{field_name} is not present on the candidate. {note}"

    return FieldValidationRecord(
        status=status,
        source_url=source_url,
        checked_at=checked_at,
        notes=field_note,
    )


def _contact_record_for_access_failure(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    note: str,
) -> ContactValidationRecord:
    if _has_text(field_value):
        status = "failed"
        field_note = note
    else:
        status = "missing"
        field_note = f"{field_name} is not present on the candidate. {note}"

    return ContactValidationRecord(
        status=status,
        source_url=source_url,
        checked_at=checked_at,
        notes=field_note,
    )


def _field_record_from_source_text(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    source_text: str,
    context_values: tuple[str, ...] = (),
) -> tuple[FieldValidationRecord, str | None]:
    if not _has_text(field_value):
        return (
            FieldValidationRecord(
                status="missing",
                source_url=source_url,
                checked_at=checked_at,
                notes=f"{field_name} is not present on the candidate.",
            ),
            None,
        )

    snippet = _find_evidence_snippet(source_text, field_value)
    if snippet:
        return (
            FieldValidationRecord(
                status="supported",
                source_url=source_url,
                evidence_snippet=snippet,
                checked_at=checked_at,
                notes=f"Direct text support found for {field_name}.",
            ),
            snippet,
        )

    if field_name == "title":
        role_snippet = _find_title_role_evidence_snippet(
            source_text,
            field_value,
            context_values=context_values,
        )
        if role_snippet:
            return (
                FieldValidationRecord(
                    status="supported",
                    source_url=source_url,
                    evidence_snippet=role_snippet,
                    checked_at=checked_at,
                    notes="Role-family text support found for title.",
                ),
                role_snippet,
            )

    return (
        FieldValidationRecord(
            status="unsupported",
            source_url=source_url,
            checked_at=checked_at,
            notes=f"No direct text support found for {field_name}.",
        ),
        None,
    )


def _contact_record_from_source_text(
    field_name: str,
    field_value: Any,
    *,
    source_url: str,
    checked_at: str,
    source_text: str,
) -> tuple[ContactValidationRecord, str | None]:
    if not _has_text(field_value):
        return (
            ContactValidationRecord(
                status="missing",
                source_url=source_url,
                checked_at=checked_at,
                notes=f"{field_name} is not present on the candidate.",
            ),
            None,
        )

    snippet = _find_evidence_snippet(source_text, field_value)
    if snippet:
        return (
            ContactValidationRecord(
                status="verified_found",
                source_url=source_url,
                evidence_snippet=snippet,
                checked_at=checked_at,
                notes=f"Direct text support found for {field_name}.",
            ),
            snippet,
        )

    return (
        ContactValidationRecord(
            status="unsupported",
            source_url=source_url,
            checked_at=checked_at,
            notes=f"No direct text support found for {field_name}.",
        ),
        None,
    )


def _candidate_field_values(candidate: Candidate) -> dict[str, Any]:
    return {
        "name": getattr(candidate, "name", None),
        "title": getattr(candidate, "title", None),
        "organization": getattr(candidate, "organization", None),
        "email": getattr(candidate, "email", None),
        "phone": getattr(candidate, "phone", None),
    }


def _build_missing_source_validation(candidate: Candidate, *, checked_at: str) -> CandidateValidation:
    field_values = _candidate_field_values(candidate)
    return CandidateValidation(
        name=_field_record_for_missing_source("name", field_values["name"], checked_at=checked_at),
        title=_field_record_for_missing_source("title", field_values["title"], checked_at=checked_at),
        organization=_field_record_for_missing_source(
            "organization", field_values["organization"], checked_at=checked_at
        ),
        email=_contact_record_for_missing_source("email", field_values["email"], checked_at=checked_at),
        phone=_contact_record_for_missing_source("phone", field_values["phone"], checked_at=checked_at),
        source=FieldValidationRecord(
            status="missing",
            source_url=None,
            checked_at=checked_at,
            notes="source_url was not provided.",
        ),
    )


def _build_access_failure_validation(
    candidate: Candidate,
    *,
    source_url: str,
    checked_at: str,
    note: str,
) -> CandidateValidation:
    field_values = _candidate_field_values(candidate)
    return CandidateValidation(
        name=_field_record_for_access_failure("name", field_values["name"], source_url=source_url, checked_at=checked_at, note=note),
        title=_field_record_for_access_failure(
            "title", field_values["title"], source_url=source_url, checked_at=checked_at, note=note
        ),
        organization=_field_record_for_access_failure(
            "organization", field_values["organization"], source_url=source_url, checked_at=checked_at, note=note
        ),
        email=_contact_record_for_access_failure("email", field_values["email"], source_url=source_url, checked_at=checked_at, note=note),
        phone=_contact_record_for_access_failure("phone", field_values["phone"], source_url=source_url, checked_at=checked_at, note=note),
        source=FieldValidationRecord(
            status="failed",
            source_url=source_url,
            checked_at=checked_at,
            notes=note,
        ),
    )


def _build_source_text_validation(
    candidate: Candidate,
    *,
    resolved_url: str,
    status_code: int,
    checked_at: str,
    source_text: str,
) -> CandidateValidation:
    field_values = _candidate_field_values(candidate)
    field_records: dict[str, FieldValidationRecord] = {}
    supported_fields: list[str] = []
    best_snippet: str | None = None

    for field_name in ("name", "title", "organization", "email", "phone"):
        if field_name in {"email", "phone"}:
            record, snippet = _contact_record_from_source_text(
                field_name,
                field_values[field_name],
                source_url=resolved_url,
                checked_at=checked_at,
                source_text=source_text,
            )
        else:
            record, snippet = _field_record_from_source_text(
                field_name,
                field_values[field_name],
                source_url=resolved_url,
                checked_at=checked_at,
                source_text=source_text,
                context_values=(
                    str(field_values["name"] or ""),
                    str(field_values["organization"] or ""),
                ),
            )
        field_records[field_name] = record
        if record.status in _SUPPORTED_SOURCE_FIELD_STATUSES:
            supported_fields.append(field_name)
            if best_snippet is None:
                best_snippet = snippet

    source_status = "supported" if supported_fields else "unsupported"
    matched_fields = ",".join(supported_fields) if supported_fields else "none"
    source_notes = f"http_status={status_code} resolved_url={resolved_url} matched_fields={matched_fields}"

    return CandidateValidation(
        name=field_records["name"],
        title=field_records["title"],
        organization=field_records["organization"],
        email=field_records["email"],
        phone=field_records["phone"],
        source=FieldValidationRecord(
            status=source_status,
            source_url=resolved_url,
            evidence_snippet=best_snippet,
            checked_at=checked_at,
            notes=source_notes,
        ),
    )


class UnsafeSourceUrlError(ValueError):
    """Raised when a candidate source URL fails scheme, hostname, or SSRF IP checks."""


class SourceResponseTooLargeError(ValueError):
    """Raised when an upstream source response exceeds MAX_SOURCE_RESPONSE_BYTES."""


def _is_forbidden_ip(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(addr, ipaddress.IPv6Address):
        if addr.ipv4_mapped is not None and _is_forbidden_ip(addr.ipv4_mapped):
            return True
        if addr in _IPV6_ULA_NETWORK or addr in _FLY_INTERNAL_NETWORK:
            return True
    elif addr in _CGNAT_NETWORK:
        return True

    return (
        addr.is_loopback
        or addr.is_private
        or addr.is_link_local
        or addr.is_multicast
        or addr.is_unspecified
        or addr.is_reserved
        or not addr.is_global
    )


def resolve_host_ips(hostname: str, port: int) -> list[str]:
    infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    ips: list[str] = []
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        raw_ip = str(sockaddr[0]).split("%", 1)[0]
        if raw_ip and raw_ip not in ips:
            ips.append(raw_ip)
    return ips


async def _assert_safe_http_url(url: str) -> None:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    if scheme not in _ALLOWED_SCHEMES:
        raise UnsafeSourceUrlError(f"disallowed_scheme:{scheme or 'missing'}")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeSourceUrlError("credentials_in_url_disallowed")

    raw_host = parsed.hostname
    if not raw_host:
        raise UnsafeSourceUrlError("missing_hostname")

    hostname = raw_host.rstrip(".").lower().split("%", 1)[0]
    if not hostname:
        raise UnsafeSourceUrlError("missing_hostname")
    if (
        hostname in {"localhost", "metadata.google.internal"}
        or hostname.endswith(_FORBIDDEN_HOST_SUFFIXES)
    ):
        raise UnsafeSourceUrlError(f"forbidden_hostname:{hostname}")

    try:
        literal_ip = ipaddress.ip_address(hostname)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if _is_forbidden_ip(literal_ip):
            raise UnsafeSourceUrlError(f"forbidden_ip:{literal_ip}")
        return

    try:
        port = parsed.port or (443 if scheme == "https" else 80)
    except ValueError as exc:
        raise UnsafeSourceUrlError("invalid_port") from exc

    try:
        resolved_ips = await asyncio.to_thread(resolve_host_ips, hostname, port)
    except OSError as exc:
        raise UnsafeSourceUrlError(f"dns_resolution_failed:{exc.__class__.__name__}") from exc

    if not resolved_ips:
        raise UnsafeSourceUrlError("dns_resolution_empty")

    for raw_ip in resolved_ips:
        try:
            addr = ipaddress.ip_address(raw_ip)
        except ValueError as exc:
            raise UnsafeSourceUrlError(f"invalid_resolved_ip:{raw_ip}") from exc
        if _is_forbidden_ip(addr):
            raise UnsafeSourceUrlError(f"forbidden_resolved_ip:{addr}")


def _check_content_length_header(headers: Any, *, max_bytes: int) -> None:
    if headers is None or not hasattr(headers, "get"):
        return
    raw_len = headers.get("content-length")
    if not raw_len:
        return
    try:
        parsed_len = int(str(raw_len).strip())
    except ValueError:
        return
    if parsed_len > max_bytes:
        raise SourceResponseTooLargeError(f"content_length={parsed_len} exceeds max_bytes={max_bytes}")


async def _fetch_safe_source_response(
    client: Any,
    source_url: str,
    *,
    max_bytes: int = MAX_SOURCE_RESPONSE_BYTES,
    max_redirects: int = MAX_SOURCE_REDIRECT_HOPS,
) -> tuple[int | Any, str, str]:
    current_url = source_url.strip()

    for hop in range(max_redirects + 1):
        await _assert_safe_http_url(current_url)

        if hasattr(client, "stream"):
            async with client.stream("GET", current_url, follow_redirects=False) as response:
                status_code = getattr(response, "status_code", None)
                resolved_url = str(getattr(response, "url", current_url) or current_url)
                headers = getattr(response, "headers", None)

                if status_code in _REDIRECT_STATUS_CODES:
                    location = headers.get("location") if headers is not None and hasattr(headers, "get") else None
                    if not location:
                        raise UnsafeSourceUrlError("redirect_missing_location")
                    if hop >= max_redirects:
                        raise UnsafeSourceUrlError(f"max_redirects_exceeded:{max_redirects}")
                    current_url = urljoin(resolved_url, str(location).strip())
                    continue

                if resolved_url != current_url:
                    await _assert_safe_http_url(resolved_url)

                if not isinstance(status_code, int) or status_code < 200 or status_code >= 300:
                    return status_code, resolved_url, ""

                _check_content_length_header(headers, max_bytes=max_bytes)
                buf = bytearray()
                async for chunk in response.aiter_bytes():
                    buf.extend(chunk)
                    if len(buf) > max_bytes:
                        raise SourceResponseTooLargeError(f"response_body_exceeded:{max_bytes}")

                encoding = getattr(response, "encoding", None) or "utf-8"
                try:
                    text_body = buf.decode(encoding, errors="replace")
                except LookupError:
                    text_body = buf.decode("utf-8", errors="replace")
                return status_code, resolved_url, text_body

        response = await client.get(current_url, follow_redirects=False)
        status_code = getattr(response, "status_code", None)
        resolved_url = str(getattr(response, "url", current_url) or current_url)
        headers = getattr(response, "headers", None)

        if status_code in _REDIRECT_STATUS_CODES:
            location = headers.get("location") if headers is not None and hasattr(headers, "get") else None
            if not location:
                raise UnsafeSourceUrlError("redirect_missing_location")
            if hop >= max_redirects:
                raise UnsafeSourceUrlError(f"max_redirects_exceeded:{max_redirects}")
            current_url = urljoin(resolved_url, str(location).strip())
            continue

        if resolved_url != current_url:
            await _assert_safe_http_url(resolved_url)

        if not isinstance(status_code, int) or status_code < 200 or status_code >= 300:
            return status_code, resolved_url, ""

        _check_content_length_header(headers, max_bytes=max_bytes)
        raw_content = getattr(response, "content", None)
        if isinstance(raw_content, (bytes, bytearray)) and len(raw_content) > max_bytes:
            raise SourceResponseTooLargeError(f"response_body_exceeded:{max_bytes}")
        text_body = str(getattr(response, "text", "") or "")
        if len(text_body.encode("utf-8", errors="replace")) > max_bytes:
            raise SourceResponseTooLargeError(f"response_body_exceeded:{max_bytes}")
        return status_code, resolved_url, text_body

    raise UnsafeSourceUrlError(f"max_redirects_exceeded:{max_redirects}")


async def _validate_candidate_source_with_client(
    candidate: Candidate,
    *,
    client: Any,
    source_url: str,
    checked_at: str,
) -> CandidateValidation:
    try:
        status_code, resolved_url, raw_source_text = await _fetch_safe_source_response(
            client,
            source_url,
        )
    except UnsafeSourceUrlError as exc:
        return _build_access_failure_validation(
            candidate,
            source_url=source_url,
            checked_at=checked_at,
            note=f"ssrf_blocked={exc}",
        )
    except SourceResponseTooLargeError as exc:
        return _build_access_failure_validation(
            candidate,
            source_url=source_url,
            checked_at=checked_at,
            note=f"response_too_large={exc}",
        )
    except Exception as exc:  # noqa: BLE001
        return _build_access_failure_validation(
            candidate,
            source_url=source_url,
            checked_at=checked_at,
            note=f"fetch_error={exc.__class__.__name__}: {exc}",
        )

    if not isinstance(status_code, int):
        return _build_access_failure_validation(
            candidate,
            source_url=resolved_url,
            checked_at=checked_at,
            note=f"fetch_error=invalid_status_code:{status_code!r}",
        )

    if status_code < 200 or status_code >= 300:
        return _build_access_failure_validation(
            candidate,
            source_url=resolved_url,
            checked_at=checked_at,
            note=f"http_status={status_code} resolved_url={resolved_url}",
        )

    source_text = _normalize_source_text(raw_source_text)
    return _build_source_text_validation(
        candidate,
        resolved_url=resolved_url,
        status_code=status_code,
        checked_at=checked_at,
        source_text=source_text,
    )


async def validate_candidate_source(candidate: Candidate, *, client: Any | None = None) -> CandidateValidation:
    checked_at = _utc_now_iso()
    source_url = getattr(candidate, "source_url", None)

    if not _has_text(source_url):
        return _build_missing_source_validation(candidate, checked_at=checked_at)

    try:
        if client is None:
            async with httpx.AsyncClient(
                timeout=SOURCE_VALIDATION_TIMEOUT_SECONDS,
                follow_redirects=False,
            ) as async_client:
                return await _validate_candidate_source_with_client(
                    candidate,
                    client=async_client,
                    source_url=source_url,
                    checked_at=checked_at,
                )
        return await _validate_candidate_source_with_client(
            candidate,
            client=client,
            source_url=source_url,
            checked_at=checked_at,
        )
    except Exception as exc:  # noqa: BLE001  # pragma: no cover - defensive guard for unexpected validator bugs
        return _build_access_failure_validation(
            candidate,
            source_url=source_url,
            checked_at=checked_at,
            note=f"validator_error={exc.__class__.__name__}: {exc}",
        )
