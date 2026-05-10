import pytest
from pydantic import ValidationError

from core.models import FailedCandidate, Lead, NotFoundCandidate, OrganizationOnlyCandidate
from core.orchestrator import SYSTEM_PROMPT


def test_lead_model():
    lead_data = {
        "candidate_category": "person_lead",
        "name": "John Doe",
        "title": "IT Director",
        "organization": "Test Org",
        "email": "john@test.org",
        "email_status": "Found",
        "source_url": "https://test.org",
        "confidence": 0.9,
        "why_target": "Fits ICP",
        "icebreaker": "Hello John",
        "fit_score": 0.9,
        "evidence_score": 0.8,
        "contact_score": 0.7,
        "gate_passed": True,
        "explanation": "High confidence lead",
    }
    lead = Lead(**lead_data)
    assert lead.candidate_category == "person_lead"
    assert lead.name == "John Doe"
    assert lead.gate_passed is True


@pytest.mark.parametrize("name", ["Sarah Chen", "Jean-Luc Picard", "Dr. Mary O'Brien"])
def test_lead_accepts_real_names(name):
    lead = Lead(
        name=name,
        title="IT Director",
        organization="Test Org",
        email="",
        email_status="Missing",
        source_url="https://test.org",
        confidence=0.9,
        why_target="Fits ICP",
        icebreaker="Hello there",
        fit_score=0.9,
        evidence_score=0.8,
        contact_score=0.7,
        gate_passed=True,
        explanation="High confidence lead",
    )
    assert lead.name == name


@pytest.mark.parametrize("name", ["Director of Technology", "VP Engineering", "John", ""])
def test_lead_rejects_role_names(name):
    with pytest.raises(ValidationError, match=r"Lead\.name"):
        Lead(
            name=name,
            title="IT Director",
            organization="Test Org",
            email="",
            email_status="Missing",
            source_url="https://test.org",
            confidence=0.9,
            why_target="Fits ICP",
            icebreaker="Hello there",
            fit_score=0.9,
            evidence_score=0.8,
            contact_score=0.7,
            gate_passed=True,
            explanation="High confidence lead",
        )


@pytest.mark.parametrize("name", ["Example Corp", "Albuquerque Public Schools", "Mesa Public Schools"])
def test_lead_rejects_organization_like_names(name):
    with pytest.raises(ValidationError, match=r"Lead\.name"):
        Lead(
            name=name,
            title="IT Director",
            organization="Test Org",
            email="",
            email_status="Missing",
            source_url="https://test.org",
            confidence=0.9,
            why_target="Fits ICP",
            icebreaker="Hello there",
            fit_score=0.9,
            evidence_score=0.8,
            contact_score=0.7,
            gate_passed=True,
            explanation="High confidence lead",
        )


@pytest.mark.parametrize("email", ["a@b.co", "", "sarah.chen+work@example.org"])
def test_lead_accepts_real_emails(email):
    lead = Lead(
        name="Sarah Chen",
        title="IT Director",
        organization="Test Org",
        email=email,
        email_status="Found" if email else "Missing",
        source_url="https://test.org",
        confidence=0.9,
        why_target="Fits ICP",
        icebreaker="Hello there",
        fit_score=0.9,
        evidence_score=0.8,
        contact_score=0.7,
        gate_passed=True,
        explanation="High confidence lead",
    )
    assert lead.email == email


@pytest.mark.parametrize("email", ["not_available@x.com", "info@x.com", "a@", "@b.co"])
def test_lead_rejects_placeholder_or_invalid_emails(email):
    with pytest.raises(ValidationError, match=r"Lead\.email"):
        Lead(
            name="Sarah Chen",
            title="IT Director",
            organization="Test Org",
            email=email,
            email_status="Found",
            source_url="https://test.org",
            confidence=0.9,
            why_target="Fits ICP",
            icebreaker="Hello there",
            fit_score=0.9,
            evidence_score=0.8,
            contact_score=0.7,
            gate_passed=True,
            explanation="High confidence lead",
        )


def test_organization_only_candidate_can_represent_an_account_without_a_person():
    candidate = OrganizationOnlyCandidate(
        organization="Example Corp",
        explanation="The account exists, but no validated person was found.",
    )

    assert candidate.candidate_category == "organization_only"
    assert candidate.organization == "Example Corp"
    assert candidate.explanation == "The account exists, but no validated person was found."


def test_organization_only_candidate_rejects_fake_person_fields():
    with pytest.raises(ValidationError):
        OrganizationOnlyCandidate(
            organization="Example Corp",
            name="Jane Doe",
            explanation="Should fail",
        )


def test_not_found_candidate_can_explain_a_searched_target():
    candidate = NotFoundCandidate(
        searched_target="Example Corp",
        explanation="No acceptable contact was found for the target account.",
    )

    assert candidate.candidate_category == "not_found"
    assert candidate.searched_target == "Example Corp"
    assert candidate.explanation == "No acceptable contact was found for the target account."


def test_not_found_candidate_rejects_fake_person_fields():
    with pytest.raises(ValidationError):
        NotFoundCandidate(
            searched_target="Example Corp",
            title="Director",
            explanation="Should fail",
        )


def test_failed_candidate_records_a_reason_without_person_fields():
    candidate = FailedCandidate(
        searched_target="Example Corp",
        failure_reason="Source was inaccessible.",
    )

    assert candidate.candidate_category == "failed"
    assert candidate.searched_target == "Example Corp"
    assert candidate.failure_reason == "Source was inaccessible."


def test_lead_field_descriptions_are_vertical_agnostic():
    assert Lead.model_fields["name"].description == "Real person's first and last name; omit the lead if unknown"
    assert Lead.model_fields["why_target"].description == (
        "1 sentence on why this role/organization fits the user's stated query intent"
    )
    assert Lead.model_fields["icebreaker"].description == (
        "A specific 1-sentence cold email opener referencing their job title, their organization, and one concrete reason their work aligns with the query intent. No template language."
    )


def test_system_prompt_restored_lost_instructions_without_voip_bias():
    assert "B2B lead research assistant" in SYSTEM_PROMPT
    assert "Include the organization name for every lead" in SYSTEM_PROMPT
    assert "Set source_url as the URL with the strongest direct evidence" in SYSTEM_PROMPT
    assert "Never invent or guess an email." in SYSTEM_PROMPT
    assert "Treat the user's query intent as the only vertical signal" in SYSTEM_PROMPT
    assert "Never use placeholders like N/A, Unknown" in SYSTEM_PROMPT
    assert "Do not inject VoIP" in SYSTEM_PROMPT
    assert "telecom, networking, or product-upgrade language" in SYSTEM_PROMPT
    assert "VoIP prospect" not in SYSTEM_PROMPT
    assert "VoIP upgrade" not in SYSTEM_PROMPT
    assert "Telecom" not in SYSTEM_PROMPT
    assert "school district / government / SMB" not in SYSTEM_PROMPT
