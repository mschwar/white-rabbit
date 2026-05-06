from core.models import Lead

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
        "explanation": "High confidence lead"
    }
    lead = Lead(**lead_data)
    assert lead.name == "John Doe"
    assert lead.gate_passed is True
