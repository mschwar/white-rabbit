from __future__ import annotations

from core.manual_oracle import (
    evaluate_manual_oracle_replay,
    load_april_nm_manual_oracle_fixture,
)


def _mock_rows_from_fixture() -> list[dict[str, str]]:
    fixture = load_april_nm_manual_oracle_fixture()
    return [
        {
            "organization": row.organization,
            "title": row.title,
            "contact_status": row.contact_status,
            "source_url": row.source_url,
            "verification_note": row.verification_note,
            "expected_tier": row.expected_tier,
            "next_action": row.next_action,
        }
        for row in fixture.rows
    ]


def test_april_nm_fixture_preserves_manual_oracle_shape_without_private_bodies():
    fixture = load_april_nm_manual_oracle_fixture()

    assert fixture.fixture_id == "april_nm_school_district_it_manual_oracle"
    assert fixture.expected_verified_contact_rows == 10
    assert fixture.expected_manual_lookup_rows == 7
    assert len(fixture.rows) == 17

    verified_rows = [row for row in fixture.rows if row.expected_tier == "high_trust_usable"]
    manual_lookup_rows = [row for row in fixture.rows if row.expected_tier == "manual_lookup"]

    assert len(verified_rows) == 10
    assert len(manual_lookup_rows) == 7
    assert {row.source_csv_shape for row in verified_rows} == {"public_emails"}
    assert {row.source_csv_shape for row in manual_lookup_rows} == {"needs_manual_lookup"}

    organizations = [row.organization for row in fixture.rows]
    assert len(organizations) == len(set(organizations))
    assert "Albuquerque Public Schools" in organizations
    assert "Rio Rancho Public Schools" in organizations
    assert "Clovis Municipal School District" in organizations

    for row in fixture.rows:
        assert row.organization
        assert row.title
        assert row.contact_status in {"verified_found", "missing"}
        assert row.source_url.startswith("https://")
        assert row.verification_note
        assert row.expected_tier in {"high_trust_usable", "manual_lookup"}
        assert "full private" not in row.verification_note.lower()


def test_manual_oracle_comparator_passes_sanitized_oracle_rows():
    rows = _mock_rows_from_fixture()
    summary = evaluate_manual_oracle_replay(rows)

    assert summary.passes() is True
    assert summary.expected_rows == 17
    assert summary.observed_rows == 17
    assert summary.verified_contact_rows == 10
    assert summary.manual_lookup_rows == 7
    assert summary.missing_organizations == ()
    assert summary.unsupported_ready_contacts == ()
    assert summary.sales_first_field_gaps == ()


def test_manual_oracle_comparator_makes_empty_current_output_failure_measurable():
    summary = evaluate_manual_oracle_replay([])

    assert summary.passes() is False
    assert summary.observed_rows == 0
    assert summary.verified_contact_rows == 0
    assert summary.manual_lookup_rows == 0
    assert len(summary.missing_organizations) == 17
    assert "Albuquerque Public Schools" in summary.missing_organizations


def test_manual_oracle_comparator_rejects_missing_contact_marked_ready():
    rows = _mock_rows_from_fixture()
    manual_lookup_row = next(row for row in rows if row["expected_tier"] == "manual_lookup")
    manual_lookup_row["expected_tier"] = "high_trust_usable"

    summary = evaluate_manual_oracle_replay(rows)

    assert summary.passes() is False
    assert summary.unsupported_ready_contacts == (
        f"{manual_lookup_row['organization']}: ready tier with missing",
    )


def test_manual_oracle_comparator_requires_sources_and_blocker_notes():
    rows = _mock_rows_from_fixture()
    rows[0]["source_url"] = ""

    manual_lookup_row = next(row for row in rows if row["expected_tier"] == "manual_lookup")
    manual_lookup_row["verification_note"] = ""
    manual_lookup_row["next_action"] = ""

    summary = evaluate_manual_oracle_replay(rows)

    assert summary.passes() is False
    assert rows[0]["organization"] in summary.missing_source_url_rows
    assert manual_lookup_row["organization"] in summary.missing_blocker_note_rows
    assert f"{manual_lookup_row['organization']}: verification_note" in summary.sales_first_field_gaps
