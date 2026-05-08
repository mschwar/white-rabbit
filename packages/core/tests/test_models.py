from core.models import Lead
from core.orchestrator import SYSTEM_PROMPT


def test_lead_model():
    lead_data = {
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
    assert lead.name == "John Doe"
    assert lead.gate_passed is True


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
