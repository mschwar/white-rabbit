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


def test_contact_evidence_accepts_person_matching_email_on_official_contact_source_without_name_snippet():
    async def fake_search(query: str, **kwargs):
        return [
            {
                "title": "Mesa Public Schools technology staff directory",
                "url": "https://www.mpsaz.org/staff/technology",
                "content": "Technology Services contacts for Mesa Public Schools include jane.smith@mpsaz.org.",
            }
        ]

    lead = _lead()

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert lead.email == "jane.smith@mpsaz.org"
    assert lead.email_status == "verified_found"
    assert lead.validation.email.source_url == "https://www.mpsaz.org/staff/technology"
    assert stats.acquired_contacts == 1


def test_contact_evidence_rejects_person_matching_email_when_official_source_lacks_contact_context():
    async def fake_search(query: str, **kwargs):
        return [
            {
                "title": "Mesa Public Schools newsletter archive",
                "url": "https://www.mpsaz.org/news/archive",
                "content": "Archived update from Mesa Public Schools includes jane.smith@mpsaz.org.",
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


def test_contact_evidence_promotes_direct_public_phone_from_official_staff_source():
    async def fake_search(query: str, **kwargs):
        return [
            {
                "title": "Mesa Public Schools staff directory",
                "url": "https://www.mpsaz.org/staff/technology",
                "content": "Jane Smith Director of Technology Mesa Public Schools Phone: (480) 472-0005",
            }
        ]

    lead = _lead()

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert lead.phone == "(480) 472-0005"
    assert lead.validation.phone.status == "verified_found"
    assert stats.acquired_contacts == 1


def test_contact_evidence_prioritizes_known_official_domain_over_external_source():
    calls: list[str] = []

    async def fake_search(query: str, **kwargs):
        calls.append(query)
        if query.startswith('site:dysart.org "Jane Smith"'):
            return [
                {
                    "title": "Dysart Unified public budget PDF",
                    "url": "https://dysart.org/cms/uploads/files/14/budget.pdf",
                    "content": (
                        "District name Dysart Unified. First Name Jane Last Name Smith "
                        "Email Address jane.smith@dysart.org Telephone Number 623-876-7180."
                    ),
                }
            ]
        return []

    lead = _lead()
    lead.name = "Jane Smith"
    lead.organization = "Dysart Unified School District"
    lead.source_url = "https://www.cosn.org/event/speakers"
    lead.validation.source.source_url = "https://www.cosn.org/event/speakers"

    stats = asyncio.run(
        acquire_contact_evidence([lead], query="Arizona K-12 technology directors", search_fn=fake_search, tavily_key="fake")
    )

    assert calls[0].startswith("site:dysart.org")
    assert lead.email == "jane.smith@dysart.org"
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


def test_contact_evidence_uses_broad_employer_queries_when_seed_source_is_third_party():
    calls: list[str] = []

    async def fake_search(query: str, **kwargs):
        calls.append(query)
        if query == '"Scot Miller" "Mr. Cooper" email phone contact':
            return [
                {
                    "title": "Mr. Cooper leadership contact",
                    "url": "https://www.mrcooper.com/leadership/security",
                    "content": (
                        "Scot Miller SVP, Chief Information Security Officer at Mr. Cooper "
                        "Email: scot.miller@mrcooper.com"
                    ),
                }
            ]
        return []

    lead = _lead()
    lead.name = "Scot Miller"
    lead.title = "SVP, Chief Information Security Officer"
    lead.organization = "Mr. Cooper"
    lead.source_url = "https://ciso-fs.coriniumintelligence.com"
    lead.validation.source.source_url = "https://ciso-fs.coriniumintelligence.com"

    stats = asyncio.run(
        acquire_contact_evidence(
            [lead],
            query="finance CISOs at financial services firms in New York",
            search_fn=fake_search,
            tavily_key="fake",
        )
    )

    assert calls[:2] == [
        'site:ciso-fs.coriniumintelligence.com "Scot Miller" "Mr. Cooper" email phone contact',
        '"Scot Miller" "Mr. Cooper" email phone contact',
    ]
    assert lead.email == "scot.miller@mrcooper.com"
    assert lead.email_status == "verified_found"
    assert lead.validation.email.status == "verified_found"
    assert stats.acquired_contacts == 1


def test_contact_evidence_promotes_pattern_from_employer_domain_source():
    async def fake_search(query: str, **kwargs):
        if query == '"Scot Miller" "Mr. Cooper" email phone contact':
            return [
                {
                    "title": "Mr. Cooper security leadership contacts",
                    "url": "https://www.mrcooper.com/security/contact",
                    "content": (
                        "Mr. Cooper security leadership uses first.last@mrcooper.com. "
                        "Scot Miller is SVP, Chief Information Security Officer."
                    ),
                }
            ]
        return []

    lead = _lead()
    lead.name = "Scot Miller"
    lead.title = "SVP, Chief Information Security Officer"
    lead.organization = "Mr. Cooper"
    lead.source_url = "https://ciso-fs.coriniumintelligence.com"
    lead.validation.source.source_url = "https://ciso-fs.coriniumintelligence.com"

    stats = asyncio.run(
        acquire_contact_evidence(
            [lead],
            query="finance CISOs at financial services firms in New York",
            search_fn=fake_search,
            tavily_key="fake",
        )
    )

    assert lead.email == "scot.miller@mrcooper.com"
    assert lead.email_status == "deduced_with_pattern_evidence"
    assert lead.validation.email.status == "deduced_with_pattern_evidence"
    assert stats.acquired_contacts == 1


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
