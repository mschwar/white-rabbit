import pytest
from pydantic import ValidationError

from core.models import CandidateValidation, ContactValidationRecord, Lead


def _make_lead(*, email_status: str) -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Albuquerque Public Schools",
        email="jane.smith@aps.edu",
        email_status=email_status,
        source_url="https://aps.edu/tech",
        confidence=0.9,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed APS is scaling its technology leadership.",
        fit_score=0.9,
        evidence_score=0.8,
        contact_score=0.7,
        gate_passed=True,
        explanation="Strong district fit with current leadership evidence and usable email.",
    )


@pytest.mark.parametrize(
    ("legacy_status", "expected_status"),
    [
        ("Found", "verified_found"),
        ("Deduced", "deduced_with_pattern_evidence"),
        ("Missing", "missing"),
    ],
)
def test_lead_normalizes_legacy_contact_status_labels(legacy_status: str, expected_status: str):
    lead = _make_lead(email_status=legacy_status)

    assert lead.email_status == expected_status


@pytest.mark.parametrize(
    "contact_status",
    [
        "verified_found",
        "deduced_with_pattern_evidence",
        "missing",
        "failed",
        "unsupported",
    ],
)
def test_lead_accepts_contact_status_values(contact_status: str):
    lead = _make_lead(email_status=contact_status)

    assert lead.email_status == contact_status


def test_lead_rejects_unknown_contact_status():
    with pytest.raises(ValidationError, match=r"email_status"):
        _make_lead(email_status="guessed")


def test_candidate_validation_defaults_contact_fields_to_unsupported():
    validation = CandidateValidation()

    assert validation.email.status == "unsupported"
    assert validation.phone.status == "unsupported"


@pytest.mark.parametrize(
    "status",
    [
        "verified_found",
        "deduced_with_pattern_evidence",
        "missing",
        "failed",
        "unsupported",
    ],
)
def test_contact_validation_record_accepts_contact_status_values(status: str):
    record = ContactValidationRecord(status=status)

    assert record.status == status
