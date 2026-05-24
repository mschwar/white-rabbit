from core.lead_quality_policy import (
    lead_has_contact_support,
    lead_has_persona_support,
    lead_is_ready_eligible,
    ready_blocker_for_candidate,
)
from core.models import CandidateValidation, ContactValidationRecord, FieldValidationRecord, Lead


def _field(status: str = "supported") -> FieldValidationRecord:
    return FieldValidationRecord(
        status=status,
        source_url="https://district.example.edu/staff",
        evidence_snippet=f"{status} evidence",
        checked_at="2026-05-24T12:00:00Z",
        notes=f"{status} notes",
    )


def _contact(status: str = "verified_found") -> ContactValidationRecord:
    return ContactValidationRecord(
        status=status,
        source_url="https://district.example.edu/staff",
        evidence_snippet=f"{status} contact evidence",
        checked_at="2026-05-24T12:00:00Z",
        notes=f"{status} notes",
    )


def _lead(*, title_status: str = "supported", email_status: str = "verified_found") -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Mesa Public Schools",
        email="jane.smith@mpsaz.org" if email_status in {"verified_found", "deduced_with_pattern_evidence"} else "",
        email_status=email_status,
        source_url="https://www.mpsaz.org/technology",
        confidence=0.9,
        why_target="Jane leads district technology work for a target Arizona K-12 account.",
        icebreaker="I saw your technology team supports Mesa Public Schools.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.9,
        gate_passed=False,
        explanation="Source-backed Arizona K-12 technology leader.",
        validation=CandidateValidation(
            name=_field(),
            title=_field(title_status),
            organization=_field(),
            email=_contact(email_status),
            phone=_contact("missing"),
            source=_field(),
        ),
    )


def test_ready_policy_requires_persona_source_contact_and_scores():
    lead = _lead()

    assert lead_has_persona_support(lead) is True
    assert lead_has_contact_support(lead) is True
    assert lead_is_ready_eligible(lead) is True


def test_ready_policy_blocks_unsupported_contact_even_when_scores_are_high():
    lead = _lead(email_status="unsupported")

    assert lead_has_persona_support(lead) is True
    assert lead_has_contact_support(lead) is False
    assert lead_is_ready_eligible(lead) is False
    assert ready_blocker_for_candidate(lead) == "no_validated_domain_pattern"


def test_ready_policy_does_not_trust_high_trust_tier_without_required_support():
    lead = _lead(email_status="unsupported")
    lead.tier = "high_trust_usable"

    assert lead_is_ready_eligible(lead) is False
    assert ready_blocker_for_candidate(lead) == "no_validated_domain_pattern"


def test_ready_policy_reports_persona_blocker_for_wrong_or_unsupported_role():
    lead = _lead(title_status="unsupported")

    assert lead_has_persona_support(lead) is False
    assert lead_is_ready_eligible(lead) is False
    assert ready_blocker_for_candidate(lead) == "title_unsupported"
