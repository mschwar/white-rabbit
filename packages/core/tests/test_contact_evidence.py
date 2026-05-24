import asyncio

from core.contact_evidence import acquire_contact_evidence
from core.models import CandidateValidation, ContactValidationRecord, FieldValidationRecord, Lead


def _field(status: str = "supported", source_url: str = "https://www.mpsaz.org/technology") -> FieldValidationRecord:
    return FieldValidationRecord(
        status=status,
        source_url=source_url,
        evidence_snippet=f"{status} evidence",
        checked_at="2026-05-24T12:00:00Z",
        notes=f"{status} notes",
    )


def _contact(status: str = "missing") -> ContactValidationRecord:
    return ContactValidationRecord(
        status=status,
        source_url=None,
        evidence_snippet=None,
        checked_at="2026-05-24T12:00:00Z",
        notes=f"{status} contact",
    )


def _lead() -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Mesa Public Schools",
        email="",
        email_status="missing",
        source_url="https://www.mpsaz.org/technology",
        confidence=0.8,
        why_target="Jane fits the Arizona K-12 technology decision-maker target.",
        icebreaker="I saw your district technology work at Mesa Public Schools.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.1,
        gate_passed=False,
        explanation="Source-backed technology leader missing contact proof.",
        validation=CandidateValidation(
            name=_field(),
            title=_field(),
            organization=_field(),
            email=_contact(),
            phone=_contact(),
            source=_field(),
        ),
    )


def test_contact_evidence_promotes_direct_public_email_from_official_staff_source():
    calls: list[str] = []

    async def fake_search(query: str, **kwargs):
        calls.append(query)
        return [
            {
                "title": "Mesa Public Schools staff directory",
                "url": "https://www.mpsaz.org/staff/technology",
                "content": "Jane Smith Director of Technology Mesa Public Schools email jane.smith@mpsaz.org",
            }
        ]

    lead = _lead()

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert calls[0].startswith("site:mpsaz.org")
    assert lead.email == "jane.smith@mpsaz.org"
    assert lead.email_status == "verified_found"
    assert lead.validation.email.status == "verified_found"
    assert stats.acquired_contacts == 1


def test_contact_evidence_rejects_pattern_from_unrelated_domain():
    async def fake_search(query: str, **kwargs):
        return [
            {
                "title": "Mesa Public Schools contact format repost",
                "url": "https://example.net/k12-contacts",
                "content": "Mesa Public Schools staff email format is first.last@unrelated.example for technology services.",
            }
        ]

    lead = _lead()

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert lead.email == ""
    assert lead.email_status == "missing"
    assert lead.validation.email.status == "missing"
    assert "no direct person email or explicit domain pattern found" in lead.validation.email.notes
    assert stats.acquired_contacts == 0


def test_contact_evidence_rejects_direct_email_from_third_party_directory():
    async def fake_search(query: str, **kwargs):
        return [
            {
                "title": "Mesa Public Schools staff directory mirror",
                "url": "https://example.net/k12-contacts",
                "content": "Jane Smith Director of Technology Mesa Public Schools email jane.smith@mpsaz.org",
            }
        ]

    lead = _lead()

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert lead.email == ""
    assert lead.email_status == "missing"
    assert lead.validation.email.status == "missing"
    assert stats.acquired_contacts == 0


def test_contact_evidence_does_not_treat_shared_public_suffix_as_same_domain():
    async def fake_search(query: str, **kwargs):
        return [
            {
                "title": "Different district staff directory",
                "url": "https://other.k12.az.us/staff",
                "content": "Mesa Public Schools staff email format is first.last@other.k12.az.us for technology services.",
            }
        ]

    lead = _lead()
    lead.source_url = "https://mesa.k12.az.us/technology"
    lead.validation.source.source_url = "https://mesa.k12.az.us/technology"

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert lead.email == ""
    assert lead.email_status == "missing"
    assert lead.validation.email.status == "missing"
    assert stats.acquired_contacts == 0
