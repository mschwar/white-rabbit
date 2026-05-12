from __future__ import annotations

from core.manual_oracle import evaluate_manual_oracle_replay
from core.source_assisted_compiler import (
    compile_april_nm_source_assisted_replay,
    compile_source_assisted_leads,
    parse_pasted_candidate_rows,
)


def test_april_nm_source_assisted_compiler_replays_workbook_shape():
    summary = compile_april_nm_source_assisted_replay()
    payload = summary.to_payload()

    assert summary.passes() is True
    assert payload["candidate_count"] == 17
    assert payload["tier_distribution"]["high_trust_usable"] == 10
    assert payload["tier_distribution"]["manual_lookup"] == 7
    assert payload["manual_oracle_replay"]["structure_reproduced"] is True
    assert payload["manual_oracle_replay"]["unsupported_ready_contacts"] == []
    assert payload["blocked_source_urls"] == []

    replay = evaluate_manual_oracle_replay(summary.candidate_payloads)
    assert replay.passes() is True

    for row in payload["candidate_rows"]:
        assert row["source_id"]
        assert row["source_ids"] == [row["source_id"]]
        assert row["field_evidence"]["organization"]["source_id"] == row["source_id"]
        assert row["field_evidence"]["email"]["status"] == row["contact_status"]
        assert row["source_family"] not in {"generic_tavily_search", "generic_web_search", "llm_browse"}
        assert "@" not in row["email"]


def test_compiler_preserves_manual_lookup_rows_without_marking_them_ready():
    summary = compile_april_nm_source_assisted_replay()
    manual_lookup_rows = [row for row in summary.candidate_payloads if row["tier"] == "manual_lookup"]

    assert len(manual_lookup_rows) == 7
    for row in manual_lookup_rows:
        assert row["contact_status"] == "missing"
        assert row["candidate_category"] == "person_lead"
        assert row["primary_filter_reason"].startswith("REVIEW:")
        assert "CRM" in row["primary_filter_reason"]
        assert row["next_action"]


def test_compiler_accepts_seed_rows_source_packs_and_pasted_rows_with_dedupe():
    seed_rows = [
        {
            "row_id": "seed-rrps-missing",
            "organization": "Rio Rancho Public Schools",
            "title": "Technology leadership contact",
            "contact_status": "missing",
            "source_url": "https://www.rrps.net/apps/staff/",
            "verification_note": "Seed row needs direct email lookup.",
            "expected_tier": "manual_lookup",
            "next_action": "Open staff directory.",
        }
    ]
    source_packs = [
        {
            "source_id": "pack-rrps-staff",
            "url": "https://www.rrps.net/apps/staff/",
            "source_family": "district_staff_directory",
            "source_reputation_signal": "official_district",
            "supports": ["staff roster", "public contact"],
            "rows": [
                {
                    "row_id": "pack-rrps-ready",
                    "organization": "Rio Rancho Public Schools",
                    "title": "Technology leadership contact",
                    "lead_name": "Public Contact",
                    "email": "public.contact@rrps.example",
                    "contact_status": "verified_found",
                    "source_url": "https://www.rrps.net/apps/staff/",
                    "verification_note": "Source pack included public contact evidence.",
                }
            ],
        }
    ]
    pasted_text = (
        "Clovis Municipal School District | Technology director | missing | "
        "https://www.clovis-schools.org/ | Chatbot found district page but no direct email | "
        "Open district staff page."
    )

    summary = compile_source_assisted_leads(
        seed_csv_rows=seed_rows,
        source_packs=source_packs,
        pasted_text=pasted_text,
    )
    rows = summary.candidate_payloads

    assert len(rows) == 2
    assert summary.duplicate_rows == ("seed-rrps-missing",)
    ready = next(row for row in rows if row["organization"] == "Rio Rancho Public Schools")
    assert ready["tier"] == "high_trust_usable"
    assert ready["contact_status"] == "verified_found"
    assert ready["source_id"] == "pack-rrps-staff"

    manual = next(row for row in rows if row["organization"] == "Clovis Municipal School District")
    assert manual["tier"] == "manual_lookup"
    assert manual["contact_status"] == "missing"
    assert manual["next_action"] == "Open district staff page."


def test_pasted_candidate_parser_accepts_pipe_lines_and_csv():
    pipe_rows = parse_pasted_candidate_rows(
        "Albuquerque Public Schools | IT Director | missing | https://www.aps.edu/ | No email found"
    )
    csv_rows = parse_pasted_candidate_rows(
        "organization,title,contact_status,source_url\n"
        "Rio Rancho Public Schools,Technology Director,verified_found,https://www.rrps.net/apps/staff/\n"
    )

    assert pipe_rows == [
        {
            "row_id": "pasted-01",
            "organization": "Albuquerque Public Schools",
            "title": "IT Director",
            "contact_status": "missing",
            "source_url": "https://www.aps.edu/",
            "verification_note": "No email found",
            "next_action": "",
        }
    ]
    assert csv_rows[0]["organization"] == "Rio Rancho Public Schools"
