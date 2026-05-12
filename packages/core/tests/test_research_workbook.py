from __future__ import annotations

import csv
import io
import json

from core.research_workbook import (
    RESEARCH_WORKBOOK_EXPORT_HEADERS,
    build_april_nm_research_workbook_replay,
    build_research_workbook,
    build_research_workbook_csv,
    write_r09g_replay_artifact,
)


def test_april_nm_research_workbook_preserves_ready_and_manual_lookup_tiers(tmp_path):
    summary = build_april_nm_research_workbook_replay()
    payload = summary.to_payload()

    assert summary.passes() is True
    assert payload["row_count"] == 17
    assert payload["tier_distribution"]["READY_WITH_CONTACT"] == 10
    assert payload["tier_distribution"]["MANUAL_LOOKUP"] == 7
    assert payload["tier_distribution"]["REVIEW"] == 0
    assert payload["downgraded_ready_rows"] == []
    assert payload["export_headers"] == list(RESEARCH_WORKBOOK_EXPORT_HEADERS)

    ready_rows = [row for row in summary.rows if row.workbook_tier == "READY_WITH_CONTACT"]
    assert len(ready_rows) == 10
    for row in ready_rows:
        assert row.crm_ready is True
        assert row.operator_label == "READY"
        assert row.email_status == "verified_found"
        assert row.source_name_url
        assert row.source_title_url
        assert row.source_org_url
        assert row.source_email_url
        assert row.source_access_status

    manual_rows = [row for row in summary.rows if row.workbook_tier == "MANUAL_LOOKUP"]
    assert len(manual_rows) == 7
    for row in manual_rows:
        assert row.crm_ready is False
        assert row.operator_label == "MANUAL LOOKUP"
        assert row.email == ""
        assert row.email_status == "missing"
        assert row.next_action
        assert row.source_org_url
        assert "CRM import blocked" in row.validation_notes

    artifact_path = write_r09g_replay_artifact(tmp_path / "research-workbook-replay.json", summary=summary)
    artifact_payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact_payload["tier_distribution"]["READY_WITH_CONTACT"] == 10
    assert artifact_payload["tier_distribution"]["MANUAL_LOOKUP"] == 7


def test_workbook_tiering_downgrades_claimed_ready_row_without_contact_support():
    summary = build_research_workbook(
        [
            {
                "candidate_id": "bad-ready",
                "input_row_id": "input-bad-ready",
                "candidate_category": "person_lead",
                "tier": "high_trust_usable",
                "lead_name": "Unsupported Contact",
                "title": "Technology Director",
                "organization": "Unsupported Schools",
                "email": "unsupported@example.com",
                "contact_status": "missing",
                "source_url": "https://unsupported.example.edu/staff",
                "source_id": "src-unsupported",
                "source_ids": ["src-unsupported"],
                "field_evidence": {
                    "name": {
                        "status": "supported",
                        "source_url": "https://unsupported.example.edu/staff",
                        "checked_at": "2026-05-11T12:00:00Z",
                    },
                    "title": {
                        "status": "supported",
                        "source_url": "https://unsupported.example.edu/staff",
                        "checked_at": "2026-05-11T12:00:00Z",
                    },
                    "organization": {
                        "status": "supported",
                        "source_url": "https://unsupported.example.edu/staff",
                        "checked_at": "2026-05-11T12:00:00Z",
                    },
                    "email": {
                        "status": "missing",
                        "source_url": "https://unsupported.example.edu/staff",
                        "checked_at": "2026-05-11T12:00:00Z",
                    },
                    "source": {
                        "status": "supported",
                        "source_url": "https://unsupported.example.edu/staff",
                        "checked_at": "2026-05-11T12:00:00Z",
                    },
                },
                "blocker_notes": "Direct email missing.",
                "next_action": "Open the staff directory manually.",
            }
        ],
        source_records=[
            {
                "source_id": "src-unsupported",
                "url": "https://unsupported.example.edu/staff",
                "access_status": "supported",
                "source_family": "district_staff_directory",
                "source_reputation_signal": "official_district",
                "input_method": "test",
            }
        ],
        query="unsupported contact test",
        run_id="run-unsupported",
    )

    row = summary.rows[0]
    assert row.workbook_tier == "MANUAL_LOOKUP"
    assert row.crm_ready is False
    assert row.email == ""
    assert row.email_status == "missing"
    assert summary.downgraded_ready_rows == ("bad-ready",)
    assert "CRM import blocked" in row.validation_notes
    assert summary.passes() is True


def test_workbook_export_csv_preserves_not_found_and_audit_columns():
    source_url = "https://district.example.edu/staff"
    summary = build_research_workbook(
        [
            {
                "candidate_id": "ready-1",
                "candidate_category": "person_lead",
                "tier": "high_trust_usable",
                "lead_name": "Jane Smith",
                "title": "Technology Director",
                "organization": "District Example",
                "email": "jane.smith@district.example",
                "contact_status": "verified_found",
                "source_url": source_url,
                "source_id": "src-district",
                "source_ids": ["src-district"],
                "fit_score": 0.91,
                "evidence_score": 0.85,
                "contact_score": 0.8,
                "field_evidence": _field_evidence(source_url, "verified_found"),
                "verification_note": "Official staff page supports this row.",
            },
            {
                "candidate_id": "missing-1",
                "candidate_category": "not_found",
                "tier": "not_found",
                "organization": "Missing District",
                "searched_target": "Missing District technology contact",
                "contact_status": "missing",
                "source_url": "https://missing.example.edu",
                "source_id": "src-missing",
                "source_ids": ["src-missing"],
                "field_evidence": _field_evidence("https://missing.example.edu", "missing"),
                "verification_note": "Searched official source and found no acceptable contact.",
            },
            {
                "candidate_id": "failed-1",
                "candidate_category": "failed",
                "tier": "failed",
                "organization": "Failed District",
                "searched_target": "Failed District technology contact",
                "contact_status": "failed",
                "source_url": "https://failed.example.edu",
                "source_id": "src-failed",
                "source_ids": ["src-failed"],
                "field_evidence": _field_evidence("https://failed.example.edu", "failed"),
                "verification_note": "Source contradicted the candidate.",
                "blocker_notes": "Wrong persona.",
            },
        ],
        source_records=[
            {
                "source_id": "src-district",
                "url": source_url,
                "access_status": "supported",
                "source_family": "district_staff_directory",
                "source_reputation_signal": "official_district",
                "input_method": "source_pack",
            },
            {
                "source_id": "src-missing",
                "url": "https://missing.example.edu",
                "access_status": "supported",
                "source_family": "district_homepage",
                "source_reputation_signal": "official_district",
                "input_method": "source_pack",
            },
            {
                "source_id": "src-failed",
                "url": "https://failed.example.edu",
                "access_status": "supported",
                "source_family": "district_homepage",
                "source_reputation_signal": "official_district",
                "input_method": "source_pack",
            },
        ],
        query="K-12 IT directors in New Mexico",
        run_id="run-csv",
    )

    csv_text = build_research_workbook_csv(summary.rows)
    parsed = list(csv.DictReader(io.StringIO(csv_text)))

    assert csv_text.splitlines()[0].startswith("query,run_id,rank,workbook_tier,operator_label")
    assert parsed[0]["workbook_tier"] == "READY_WITH_CONTACT"
    assert parsed[0]["crm_ready"] == "yes"
    assert parsed[0]["email"] == "jane.smith@district.example"
    assert parsed[0]["source_email_url"] == source_url
    assert parsed[0]["source_access_status"] == "supported"
    assert parsed[0]["fit_score"] == "0.91"

    assert parsed[1]["workbook_tier"] == "NOT_FOUND"
    assert parsed[1]["crm_ready"] == "no"
    assert parsed[1]["organization"] == "Missing District"
    assert parsed[1]["source_org_url"] == "https://missing.example.edu"
    assert "CRM import blocked" in parsed[1]["validation_notes"]

    assert parsed[2]["workbook_tier"] == "FAILED"
    assert parsed[2]["email"] == ""
    assert parsed[2]["blocker_notes"] == "Wrong persona."


def _field_evidence(source_url: str, email_status: str) -> dict[str, dict[str, str]]:
    return {
        "name": {"status": "supported", "source_url": source_url, "checked_at": "2026-05-11T12:00:00Z"},
        "title": {"status": "supported", "source_url": source_url, "checked_at": "2026-05-11T12:00:00Z"},
        "organization": {"status": "supported", "source_url": source_url, "checked_at": "2026-05-11T12:00:00Z"},
        "email": {"status": email_status, "source_url": source_url, "checked_at": "2026-05-11T12:00:00Z"},
        "source": {"status": "supported", "source_url": source_url, "checked_at": "2026-05-11T12:00:00Z"},
    }
