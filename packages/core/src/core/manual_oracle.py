from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_APRIL_NM_FIXTURE_PATH = (
    _REPO_ROOT / "packages/core/tests/fixtures/april_nm_manual_oracle.json"
)

READY_TIERS = {"high_trust_usable", "ready", "READY"}
MANUAL_LOOKUP_TIERS = {"manual_lookup", "review", "REVIEW"}
CRM_READY_CONTACT_STATUSES = {"verified_found", "deduced_with_pattern_evidence"}
MANUAL_LOOKUP_CONTACT_STATUSES = {"missing", "unsupported"}


@dataclass(frozen=True, slots=True)
class ManualOracleRow:
    row_id: str
    source_csv_shape: str
    organization: str
    title: str
    contact_status: str
    source_url: str
    verification_note: str
    expected_tier: str
    next_action: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> ManualOracleRow:
        return cls(
            row_id=str(payload["row_id"]),
            source_csv_shape=str(payload["source_csv_shape"]),
            organization=str(payload["organization"]),
            title=str(payload["title"]),
            contact_status=str(payload["contact_status"]),
            source_url=str(payload["source_url"]),
            verification_note=str(payload["verification_note"]),
            expected_tier=str(payload["expected_tier"]),
            next_action=str(payload.get("next_action", "")),
        )


@dataclass(frozen=True, slots=True)
class ManualOracleFixture:
    fixture_id: str
    source_evidence_note: str
    thresholds: Mapping[str, int]
    required_sales_fields: tuple[str, ...]
    rows: tuple[ManualOracleRow, ...]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> ManualOracleFixture:
        return cls(
            fixture_id=str(payload["fixture_id"]),
            source_evidence_note=str(payload["source_evidence_note"]),
            thresholds={str(key): int(value) for key, value in dict(payload["thresholds"]).items()},
            required_sales_fields=tuple(str(field) for field in payload["required_sales_fields"]),
            rows=tuple(ManualOracleRow.from_payload(row) for row in payload["rows"]),
        )

    @property
    def expected_verified_contact_rows(self) -> int:
        return self.thresholds["expected_verified_contact_rows"]

    @property
    def expected_manual_lookup_rows(self) -> int:
        return self.thresholds["expected_manual_lookup_rows"]


@dataclass(frozen=True, slots=True)
class ManualOracleReplaySummary:
    fixture_id: str
    expected_rows: int
    observed_rows: int
    expected_verified_contact_rows: int
    verified_contact_rows: int
    expected_manual_lookup_rows: int
    manual_lookup_rows: int
    represented_organizations: tuple[str, ...]
    missing_organizations: tuple[str, ...]
    duplicate_organizations: tuple[str, ...]
    missing_source_url_rows: tuple[str, ...]
    missing_blocker_note_rows: tuple[str, ...]
    sales_first_field_gaps: tuple[str, ...]
    unsupported_ready_contacts: tuple[str, ...]
    structure_reproduced: bool

    def passes(self) -> bool:
        return self.structure_reproduced

    def to_payload(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "expected_rows": self.expected_rows,
            "observed_rows": self.observed_rows,
            "expected_verified_contact_rows": self.expected_verified_contact_rows,
            "verified_contact_rows": self.verified_contact_rows,
            "expected_manual_lookup_rows": self.expected_manual_lookup_rows,
            "manual_lookup_rows": self.manual_lookup_rows,
            "represented_organizations": list(self.represented_organizations),
            "missing_organizations": list(self.missing_organizations),
            "duplicate_organizations": list(self.duplicate_organizations),
            "missing_source_url_rows": list(self.missing_source_url_rows),
            "missing_blocker_note_rows": list(self.missing_blocker_note_rows),
            "sales_first_field_gaps": list(self.sales_first_field_gaps),
            "unsupported_ready_contacts": list(self.unsupported_ready_contacts),
            "structure_reproduced": self.structure_reproduced,
        }


def load_april_nm_manual_oracle_fixture(
    path: Path | None = None,
) -> ManualOracleFixture:
    fixture_path = path or DEFAULT_APRIL_NM_FIXTURE_PATH
    return ManualOracleFixture.from_payload(json.loads(fixture_path.read_text(encoding="utf-8")))


def evaluate_manual_oracle_replay(
    rows: list[Mapping[str, Any]],
    fixture: ManualOracleFixture | None = None,
) -> ManualOracleReplaySummary:
    fixture = fixture or load_april_nm_manual_oracle_fixture()
    rows_by_organization: dict[str, list[Mapping[str, Any]]] = {}

    for row in rows:
        organization = _normalized_text(row.get("organization"))
        if not organization:
            continue
        rows_by_organization.setdefault(organization.lower(), []).append(row)

    verified_contact_rows = 0
    manual_lookup_rows = 0
    represented_organizations: list[str] = []
    missing_organizations: list[str] = []
    duplicate_organizations: list[str] = []
    missing_source_url_rows: list[str] = []
    missing_blocker_note_rows: list[str] = []
    sales_first_field_gaps: list[str] = []
    unsupported_ready_contacts: list[str] = []

    for expected in fixture.rows:
        matches = rows_by_organization.get(expected.organization.lower(), [])
        if not matches:
            missing_organizations.append(expected.organization)
            continue
        if len(matches) > 1:
            duplicate_organizations.append(expected.organization)

        row = matches[0]
        represented_organizations.append(expected.organization)

        if not _source_url(row):
            missing_source_url_rows.append(expected.organization)

        if not _blocker_note(row):
            sales_first_field_gaps.append(f"{expected.organization}: verification_note")

        for field_name in fixture.required_sales_fields:
            if not _has_sales_field(row, field_name):
                sales_first_field_gaps.append(f"{expected.organization}: {field_name}")

        tier = _tier(row)
        contact_status = _contact_status(row)
        if tier in READY_TIERS and contact_status not in CRM_READY_CONTACT_STATUSES:
            unsupported_ready_contacts.append(
                f"{expected.organization}: ready tier with {contact_status or 'missing contact status'}"
            )

        if expected.expected_tier in READY_TIERS:
            if (
                tier in READY_TIERS
                and contact_status in CRM_READY_CONTACT_STATUSES
                and _source_url(row)
                and _blocker_note(row)
            ):
                verified_contact_rows += 1
            continue

        if expected.expected_tier == "manual_lookup":
            if not _blocker_note(row):
                missing_blocker_note_rows.append(expected.organization)
                continue
            if (
                tier in MANUAL_LOOKUP_TIERS
                and contact_status in MANUAL_LOOKUP_CONTACT_STATUSES
                and _source_url(row)
            ):
                manual_lookup_rows += 1

    structure_reproduced = (
        verified_contact_rows >= fixture.expected_verified_contact_rows
        and manual_lookup_rows >= fixture.expected_manual_lookup_rows
        and not missing_organizations
        and not duplicate_organizations
        and not missing_source_url_rows
        and not missing_blocker_note_rows
        and not sales_first_field_gaps
        and not unsupported_ready_contacts
    )

    return ManualOracleReplaySummary(
        fixture_id=fixture.fixture_id,
        expected_rows=len(fixture.rows),
        observed_rows=len(rows),
        expected_verified_contact_rows=fixture.expected_verified_contact_rows,
        verified_contact_rows=verified_contact_rows,
        expected_manual_lookup_rows=fixture.expected_manual_lookup_rows,
        manual_lookup_rows=manual_lookup_rows,
        represented_organizations=tuple(represented_organizations),
        missing_organizations=tuple(missing_organizations),
        duplicate_organizations=tuple(duplicate_organizations),
        missing_source_url_rows=tuple(missing_source_url_rows),
        missing_blocker_note_rows=tuple(missing_blocker_note_rows),
        sales_first_field_gaps=tuple(sorted(set(sales_first_field_gaps))),
        unsupported_ready_contacts=tuple(unsupported_ready_contacts),
        structure_reproduced=structure_reproduced,
    )


def _normalized_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _tier(row: Mapping[str, Any]) -> str:
    return _normalized_text(row.get("expected_tier")) or _normalized_text(row.get("tier"))


def _contact_status(row: Mapping[str, Any]) -> str:
    return _normalized_text(row.get("contact_status")) or _normalized_text(row.get("email_status"))


def _source_url(row: Mapping[str, Any]) -> str:
    return _normalized_text(row.get("source_url"))


def _blocker_note(row: Mapping[str, Any]) -> str:
    for field_name in (
        "verification_note",
        "validation_notes",
        "primary_filter_reason",
        "next_action",
        "explanation",
    ):
        value = _normalized_text(row.get(field_name))
        if value:
            return value
    return ""


def _has_sales_field(row: Mapping[str, Any], field_name: str) -> bool:
    if field_name == "contact_status":
        return bool(_contact_status(row))
    if field_name == "expected_tier":
        return bool(_tier(row))
    if field_name == "verification_note":
        return bool(_blocker_note(row))
    if field_name == "source_url":
        return bool(_source_url(row))
    return bool(_normalized_text(row.get(field_name)))
