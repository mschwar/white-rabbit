from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import pytest

from core.orchestrator import scout

FIXTURE_PATH = Path(__file__).with_name("fixtures") / "arizona_k12_voip.json"
LIVE_ENV_FLAG = "RUN_LIVE"
CHECKED_AT = "2026-05-10T12:00:00Z"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PLACEHOLDER_EMAIL_PREFIXES = (
    "not_available@",
    "noreply@",
    "no-reply@",
    "placeholder@",
    "email@",
    "info@",
    "admin@",
    "contact@",
)


@dataclass(slots=True)
class ArizonaBenchmarkSummary:
    usable_cases: int = 0
    not_found_cases: int = 0
    failed_cases: int = 0
    hit_cases: int = 0
    fake_email_count: int = 0
    unsupported_email_count: int = 0
    mismatched_cases: list[str] = field(default_factory=list)

    def passes(self, fixture: Mapping[str, Any]) -> bool:
        thresholds = fixture["thresholds"]
        return (
            self.hit_cases >= thresholds["minimum_hit_count"]
            and self.fake_email_count <= thresholds["maximum_fake_emails"]
            and self.unsupported_email_count <= thresholds["maximum_unsupported_emails"]
            and not self.mismatched_cases
        )


def _load_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _is_fake_email(value: str) -> bool:
    if not value:
        return False

    lowered = value.lower()
    if any(lowered.startswith(prefix) for prefix in PLACEHOLDER_EMAIL_PREFIXES):
        return True
    return EMAIL_RE.match(value) is None


def _infer_district(row: Mapping[str, Any], cases: list[Mapping[str, Any]]) -> str | None:
    text = " ".join(
        str(value)
        for value in (
            row.get("district"),
            row.get("organization"),
            row.get("searched_target"),
            row.get("name"),
        )
        if value
    ).lower()
    if not text:
        return None

    for case in cases:
        district = str(case["district"])
        organization = str(case["organization"])
        if district.lower() in text or organization.lower() in text:
            return district
    return None


def _build_mock_rows_from_fixture(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        district = str(case["district"])
        organization = str(case["organization"])
        annotation = str(case["workbook_annotation"])
        expected_category = str(case["expected_category"])
        expected_contact_status = str(case["expected_contact_status"])
        slug = _slugify(district)
        source_url = f"https://benchmark.local/arizona/{slug}"

        if expected_category == "person_lead":
            rows.append(
                {
                    "district": district,
                    "organization": organization,
                    "candidate_category": "person_lead",
                    "name": f"Avery {district.split()[0]}",
                    "title": str(case["target_role"]),
                    "email": f"{slug}.lead@{slug}.k12.az.us",
                    "email_status": expected_contact_status,
                    "source_url": source_url,
                    "checked_at": CHECKED_AT,
                    "workbook_annotation": annotation,
                    "explanation": f"Workbook marked {annotation}.",
                }
            )
            continue

        if expected_category == "not_found":
            rows.append(
                {
                    "district": district,
                    "organization": organization,
                    "candidate_category": "not_found",
                    "searched_target": f"{organization} {case['target_role']}",
                    "email": "",
                    "email_status": expected_contact_status,
                    "source_url": source_url,
                    "checked_at": CHECKED_AT,
                    "workbook_annotation": annotation,
                    "explanation": f"Workbook marked {annotation}.",
                }
            )
            continue

        rows.append(
            {
                "district": district,
                "organization": organization,
                "candidate_category": "failed",
                "searched_target": f"{organization} {case['target_role']}",
                "failure_reason": annotation,
                "email": "",
                "email_status": expected_contact_status,
                "source_url": source_url,
                "checked_at": CHECKED_AT,
                "workbook_annotation": annotation,
                "explanation": f"Workbook marked {annotation}.",
            }
        )

    return rows


def evaluate_arizona_benchmark(
    rows: list[Mapping[str, Any]],
    fixture: Mapping[str, Any],
) -> ArizonaBenchmarkSummary:
    summary = ArizonaBenchmarkSummary()
    cases = list(fixture["cases"])
    rows_by_district: dict[str, Mapping[str, Any]] = {}

    for row in rows:
        district = _infer_district(row, cases)
        if district is None:
            summary.mismatched_cases.append(f"unmapped row: {row!r}")
            continue

        if district in rows_by_district:
            summary.mismatched_cases.append(f"{district}: duplicate row")
            continue

        rows_by_district[district] = row

    for case in cases:
        district = str(case["district"])
        expected_category = str(case["expected_category"])
        expected_contact_status = str(case["expected_contact_status"])
        row = rows_by_district.get(district)

        if row is None:
            summary.mismatched_cases.append(f"{district}: missing row")
            continue

        actual_category = str(row.get("candidate_category", ""))
        if actual_category != expected_category:
            summary.mismatched_cases.append(
                f"{district}: expected {expected_category}, got {actual_category or 'missing'}"
            )
            continue

        email = str(row.get("email") or "")
        email_status = str(row.get("email_status") or "")

        if expected_category == "person_lead":
            if _is_fake_email(email):
                summary.fake_email_count += 1
                summary.mismatched_cases.append(f"{district}: fake email {email!r}")
                continue
            if email_status not in {"verified_found", "deduced_with_pattern_evidence"}:
                summary.unsupported_email_count += 1
                summary.mismatched_cases.append(f"{district}: unsupported email status {email_status!r}")
                continue
            summary.usable_cases += 1
            summary.hit_cases += 1
            continue

        if expected_category == "not_found":
            if email:
                if _is_fake_email(email):
                    summary.fake_email_count += 1
                else:
                    summary.unsupported_email_count += 1
                summary.mismatched_cases.append(f"{district}: not_found row carried contact {email!r}")
                continue
            if email_status not in {"missing", "unsupported"}:
                summary.unsupported_email_count += 1
                summary.mismatched_cases.append(
                    f"{district}: not_found row had status {email_status!r}"
                )
                continue
            summary.not_found_cases += 1
            summary.hit_cases += 1
            continue

        if expected_category == "failed":
            if email:
                if _is_fake_email(email):
                    summary.fake_email_count += 1
                else:
                    summary.unsupported_email_count += 1
                summary.mismatched_cases.append(f"{district}: failed row carried contact {email!r}")
                continue
            if email_status != expected_contact_status:
                summary.unsupported_email_count += 1
                summary.mismatched_cases.append(f"{district}: failed row had status {email_status!r}")
                continue
            summary.failed_cases += 1
            continue

        summary.mismatched_cases.append(f"{district}: unknown expected category {expected_category!r}")

    return summary


def test_arizona_benchmark_fixture_lists_the_target_districts_and_annotations():
    fixture = _load_fixture()

    assert fixture["benchmark_id"] == "az_k12_voip"
    assert fixture["source"].endswith("GPT output is not ground truth.")
    assert fixture["target_districts"] == [case["district"] for case in fixture["cases"]]
    assert len(fixture["cases"]) == 8
    assert fixture["thresholds"]["minimum_hit_count"] == 6

    annotations = {case["workbook_annotation"] for case in fixture["cases"]}
    statuses = {case["expected_contact_status"] for case in fixture["cases"]}

    assert {"failed email", "not-correct contact", "in CRM", "added to CRM where known"} <= annotations
    assert {
        "verified_found",
        "deduced_with_pattern_evidence",
        "missing",
        "failed",
    } <= statuses
    for district in fixture["target_districts"]:
        assert district in fixture["query"]


def test_arizona_benchmark_harness_passes_on_mocked_rows_without_fake_emails():
    fixture = _load_fixture()
    rows = _build_mock_rows_from_fixture(fixture)
    summary = evaluate_arizona_benchmark(rows, fixture)

    assert summary.usable_cases == 4
    assert summary.not_found_cases == 2
    assert summary.failed_cases == 2
    assert summary.hit_cases == 6
    assert summary.fake_email_count == 0
    assert summary.unsupported_email_count == 0
    assert summary.mismatched_cases == []
    assert summary.passes(fixture) is True


def test_arizona_benchmark_harness_rejects_fake_emails_and_wrong_categories():
    fixture = _load_fixture()
    rows = _build_mock_rows_from_fixture(fixture)

    mesa_row = next(row for row in rows if row["district"] == "Mesa")
    mesa_row["email"] = "not_available@mesa.k12.az.us"

    gilbert_row = next(row for row in rows if row["district"] == "Gilbert")
    gilbert_row["candidate_category"] = "person_lead"
    gilbert_row["email"] = "gilbert.lead@gilbert.k12.az.us"
    gilbert_row["email_status"] = "verified_found"

    summary = evaluate_arizona_benchmark(rows, fixture)

    assert summary.fake_email_count == 1
    assert summary.unsupported_email_count == 0
    assert summary.passes(fixture) is False
    assert any("Mesa" in message for message in summary.mismatched_cases)
    assert any("Gilbert" in message for message in summary.mismatched_cases)


needs_live_keys = pytest.mark.skipif(
    not os.getenv(LIVE_ENV_FLAG)
    or not os.getenv("OPENAI_API_KEY")
    or not os.getenv("TAVILY_API_KEY"),
    reason="needs RUN_LIVE and real OpenAI/Tavily keys",
)


@needs_live_keys
@pytest.mark.integration
def test_arizona_benchmark_can_run_live_when_enabled():
    fixture = _load_fixture()
    leads, _ = asyncio.run(
        scout(
            fixture["query"],
            max_leads=len(fixture["cases"]),
        )
    )

    rows = [lead.model_dump() for lead in leads]
    summary = evaluate_arizona_benchmark(rows, fixture)

    assert summary.passes(fixture) is True
