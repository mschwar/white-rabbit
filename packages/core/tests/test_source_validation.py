import asyncio
from collections.abc import AsyncIterator

import httpx
import pytest
from core import source_validation
from core.models import Lead, OrganizationOnlyCandidate
from core.source_validation import MAX_SOURCE_RESPONSE_BYTES, validate_candidate_source


@pytest.fixture(autouse=True)
def _stub_public_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        source_validation,
        "resolve_host_ips",
        lambda hostname, port: ["93.184.216.34"],
    )


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        text: str,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.text = text
        self.url = url
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}


class FakeClient:
    def __init__(
        self,
        response: FakeResponse | list[FakeResponse] | None = None,
        error: Exception | None = None,
    ) -> None:
        if isinstance(response, list):
            self.responses = list(response)
        elif response is not None:
            self.responses = [response]
        else:
            self.responses = []
        self.error = error
        self.requested_urls: list[str] = []
        self.follow_redirects: list[bool] = []

    async def get(self, url: str, follow_redirects: bool = False):
        self.requested_urls.append(url)
        self.follow_redirects.append(follow_redirects)
        if self.error is not None:
            raise self.error
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


def _make_lead(*, source_url: str = "https://example.com/source") -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Albuquerque Public Schools",
        email="jane.smith@aps.edu",
        email_status="verified_found",
        source_url=source_url,
        confidence=0.9,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed APS is scaling its technology leadership.",
        fit_score=0.9,
        evidence_score=0.8,
        contact_score=0.7,
        gate_passed=True,
        explanation="Strong district fit with current leadership evidence and usable email.",
    )


def test_validate_candidate_source_marks_verified_found_fields_from_page_content():
    candidate = _make_lead()
    client = FakeClient(
        FakeResponse(
            200,
            "Jane Smith is the Director of Technology at Albuquerque Public Schools. "
            "Reach her at jane.smith@aps.edu.",
            "https://aps.edu/leadership/jane-smith",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == [candidate.source_url]
    assert client.follow_redirects == [False]
    assert validation.source.status == "supported"
    assert validation.source.source_url == "https://aps.edu/leadership/jane-smith"
    assert validation.name.status == "supported"
    assert validation.title.status == "supported"
    assert validation.organization.status == "supported"
    assert validation.email.status == "verified_found"
    assert validation.phone.status == "missing"
    assert validation.source.checked_at.endswith("Z")
    assert "http_status=200" in validation.source.notes
    assert "matched_fields=name,title,organization,email" in validation.source.notes


def test_validate_candidate_source_marks_200_without_matches_unsupported():
    candidate = _make_lead(source_url="https://example.com/no-match")
    client = FakeClient(
        FakeResponse(
            200,
            "Example Corp publishes a generic homepage without person-specific details.",
            "https://example.com/home",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert validation.source.status == "unsupported"
    assert validation.source.source_url == "https://example.com/home"
    assert validation.name.status == "unsupported"
    assert validation.title.status == "unsupported"
    assert validation.organization.status == "unsupported"
    assert validation.email.status == "unsupported"
    assert "matched_fields=none" in validation.source.notes


def test_validate_candidate_source_supports_k12_tech_role_family_with_snippet():
    candidate = Lead(
        name="Jon Castelhano",
        title="Executive Director of Technology",
        organization="Gilbert Public Schools",
        email="",
        email_status="missing",
        source_url="https://www.gilbertschools.net/contact",
        confidence=0.8,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed Gilbert Public Schools lists a technology leadership team.",
        fit_score=0.8,
        evidence_score=0.7,
        contact_score=0.0,
        gate_passed=False,
        explanation="Official district contact page lists technology leadership.",
    )
    client = FakeClient(
        FakeResponse(
            200,
            "Contact Us - Gilbert Public Schools. Department Staff Directory. "
            "Technology Jon Castelhano CHIEF TECHNOLOGY OFFICER Donalee McIntyre "
            "EXECUTIVE ASSISTANT Scott Haase DIRECTOR - TECH INFRASTRUCTURE AND CYBERSECURITY.",
            "https://www.gilbertschools.net/contact",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert validation.name.status == "supported"
    assert validation.title.status == "supported"
    assert validation.title.evidence_snippet is not None
    assert "Jon Castelhano" in validation.title.evidence_snippet
    assert "CHIEF TECHNOLOGY OFFICER" in validation.title.evidence_snippet
    assert validation.title.notes == "Role-family text support found for title."
    assert validation.organization.status == "supported"
    assert validation.email.status == "missing"
    assert "matched_fields=name,title,organization" in validation.source.notes


@pytest.mark.parametrize("status_code", [403, 404, 999])
def test_validate_candidate_source_marks_inaccessible_sources_failed(status_code):
    candidate = _make_lead(source_url="https://example.com/blocked")
    client = FakeClient(FakeResponse(status_code, "Access denied", "https://example.com/blocked"))

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert validation.source.status == "failed"
    assert validation.source.source_url == "https://example.com/blocked"
    assert validation.name.status == "failed"
    assert validation.title.status == "failed"
    assert validation.organization.status == "failed"
    assert validation.email.status == "failed"
    assert f"http_status={status_code}" in validation.source.notes


def test_validate_candidate_source_marks_missing_source_without_network():
    candidate = OrganizationOnlyCandidate(
        organization="Example Corp",
        explanation="The account exists, but no validated person was found.",
    )
    client = FakeClient(
        FakeResponse(
            200,
            "This response should never be fetched.",
            "https://example.com/unused",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == []
    assert validation.source.status == "missing"
    assert validation.source.source_url is None
    assert validation.organization.status == "failed"
    assert validation.name.status == "missing"
    assert validation.title.status == "missing"
    assert validation.email.status == "missing"


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "file:///etc/passwd",
        "ftp://example.com/roster.csv",
        "gopher://127.0.0.1:70/_",
        "http://localhost:8000/readiness",
        "http://service.internal/admin",
        "http://127.0.0.1:8000/health",
        "http://10.0.0.5/staff",
        "http://172.16.10.2/staff",
        "http://192.168.1.1/staff",
        "http://169.254.169.254/latest/meta-data/",
        "http://100.100.100.200/latest/meta-data/",
        "http://224.0.0.1/multicast",
        "http://[::1]:8000/health",
        "http://[::ffff:169.254.169.254]/latest/meta-data/",
        "http://[fdaa:0:1234::1]:8080/internal",
        "http://[fe80::1]/link-local",
    ],
)
def test_validate_candidate_source_blocks_ssrf_schemes_and_internal_ips(unsafe_url: str):
    candidate = _make_lead(source_url=unsafe_url)
    client = FakeClient(FakeResponse(200, "secret internal data", unsafe_url))

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == []
    assert validation.source.status == "failed"
    assert "ssrf_blocked=" in (validation.source.notes or "")


@pytest.mark.parametrize(
    "resolved_ips",
    [
        ["127.0.0.1"],
        ["169.254.169.254"],
        ["fdaa:0:99::3"],
        ["93.184.216.34", "10.0.0.8"],
    ],
)
def test_validate_candidate_source_blocks_dns_rebinding_to_internal_ips(
    monkeypatch: pytest.MonkeyPatch,
    resolved_ips: list[str],
):
    monkeypatch.setattr(source_validation, "resolve_host_ips", lambda hostname, port: resolved_ips)
    candidate = _make_lead(source_url="https://attacker.example/roster")
    client = FakeClient(FakeResponse(200, "secret", "https://attacker.example/roster"))

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == []
    assert validation.source.status == "failed"
    assert "ssrf_blocked=" in (validation.source.notes or "")


@pytest.mark.parametrize(
    "redirect_target",
    [
        "http://169.254.169.254/latest/meta-data/",
        "http://[fdaa:0:1234::1]:8080/internal",
        "file:///etc/shadow",
    ],
)
def test_validate_candidate_source_blocks_ssrf_on_redirect_hops(redirect_target: str):
    candidate = _make_lead(source_url="https://example.com/start")
    client = FakeClient(
        [
            FakeResponse(
                302,
                "",
                "https://example.com/start",
                headers={"Location": redirect_target},
            ),
            FakeResponse(200, "should never reach redirect target", redirect_target),
        ]
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == ["https://example.com/start"]
    assert validation.source.status == "failed"
    assert "ssrf_blocked=" in (validation.source.notes or "")


def test_validate_candidate_source_caps_streaming_response_body_size():
    chunks_read = 0

    class OversizedByteStream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            nonlocal chunks_read
            for _ in range(10):
                chunks_read += 1
                yield b"x" * (512 * 1024)  # 512 KB per chunk; 5th chunk exceeds 2 MB

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, stream=OversizedByteStream(), request=request)

    async def _run() -> source_validation.CandidateValidation:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, follow_redirects=False) as async_client:
            return await validate_candidate_source(_make_lead(), client=async_client)

    validation = asyncio.run(_run())

    assert validation.source.status == "failed"
    assert f"response_body_exceeded:{MAX_SOURCE_RESPONSE_BYTES}" in (validation.source.notes or "")
    assert chunks_read == 5  # Stopped reading as soon as 2 MB cap was exceeded
