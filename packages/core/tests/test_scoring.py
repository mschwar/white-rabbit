from core.models import (
    CandidateValidation,
    ContactValidationRecord,
    FieldValidationRecord,
    Lead,
    NotFoundCandidate,
    OrganizationOnlyCandidate,
)
from core.orchestrator import _lead_passes_evidence_gate


def _field(status: str = "supported") -> FieldValidationRecord:
    return FieldValidationRecord(
        status=status,
        source_url="https://example.com/source",
        checked_at="2026-05-10T12:00:00Z",
        notes=f"test {status}",
    )


def _contact(status: str = "verified_found") -> ContactValidationRecord:
    return ContactValidationRecord(
        status=status,
        source_url="https://example.com/source",
        checked_at="2026-05-10T12:00:00Z",
        notes=f"test {status}",
    )


def _validation(
    *,
    name_status: str = "supported",
    title_status: str = "supported",
    organization_status: str = "supported",
    email_status: str = "verified_found",
    source_status: str = "supported",
) -> CandidateValidation:
    return CandidateValidation(
        name=_field(name_status),
        title=_field(title_status),
        organization=_field(organization_status),
        email=_contact(email_status),
        phone=_contact("missing"),
        source=_field(source_status),
    )


def _lead(
    *,
    validation: CandidateValidation | None = None,
    fit_score: float = 0.9,
    evidence_score: float = 0.9,
    contact_score: float = 0.9,
) -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Albuquerque Public Schools",
        email="jane.smith@aps.edu",
        email_status="verified_found",
        source_url="https://example.com/source",
        confidence=0.9,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed APS is scaling its technology leadership.",
        fit_score=fit_score,
        evidence_score=evidence_score,
        contact_score=contact_score,
        gate_passed=False,
        explanation="Strong district fit with current leadership evidence and usable email.",
        validation=validation or _validation(),
    )


def test_evidence_gate_passes_verified_person_lead():
    assert _lead_passes_evidence_gate(_lead()) is True


def test_evidence_gate_passes_deduced_contact_with_pattern_evidence():
    lead = _lead(validation=_validation(email_status="deduced_with_pattern_evidence"))

    assert _lead_passes_evidence_gate(lead) is True


def test_evidence_gate_blocks_wrong_persona_even_when_evidence_is_supported():
    lead = _lead(fit_score=0.2)

    assert _lead_passes_evidence_gate(lead) is False


def test_evidence_gate_blocks_unsupported_title_or_organization():
    unsupported_title = _lead(validation=_validation(title_status="unsupported"))
    unsupported_org = _lead(validation=_validation(organization_status="unsupported"))

    assert _lead_passes_evidence_gate(unsupported_title) is False
    assert _lead_passes_evidence_gate(unsupported_org) is False


def test_evidence_gate_blocks_inaccessible_source():
    lead = _lead(validation=_validation(source_status="failed"))

    assert _lead_passes_evidence_gate(lead) is False


def test_evidence_gate_blocks_fake_or_unsupported_contacts():
    failed_contact = _lead(validation=_validation(email_status="failed"))
    unsupported_contact = _lead(validation=_validation(email_status="unsupported"))
    missing_contact = _lead(validation=_validation(email_status="missing"))

    assert _lead_passes_evidence_gate(failed_contact) is False
    assert _lead_passes_evidence_gate(unsupported_contact) is False
    assert _lead_passes_evidence_gate(missing_contact) is False


def test_non_person_candidates_are_not_passable_person_leads():
    organization_only = OrganizationOnlyCandidate(
        organization="Example Corp",
        explanation="Organization found, but no usable person was validated.",
    )
    not_found = NotFoundCandidate(
        searched_target="Mesa Public Schools technology decision maker",
        organization="Mesa Public Schools",
        explanation="No acceptable contact was found.",
    )

    assert not isinstance(organization_only, Lead)
    assert not isinstance(not_found, Lead)
    assert organization_only.candidate_category == "organization_only"
    assert not_found.candidate_category == "not_found"
