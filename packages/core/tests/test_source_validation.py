import asyncio

import pytest

from core.models import Lead
from core.models import OrganizationOnlyCandidate
from core.source_validation import validate_candidate_source


class FakeResponse:
    def __init__(self, status_code: int, text: str, url: str) -> None:
        self.status_code = status_code
        self.text = text
        self.url = url


class FakeClient:
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.requested_urls: list[str] = []
        self.follow_redirects: list[bool] = []

    async def get(self, url: str, follow_redirects: bool = False):
        self.requested_urls.append(url)
        self.follow_redirects.append(follow_redirects)
        if self.error is not None:
            raise self.error
        return self.response


def _make_lead(*, source_url: str = "https://example.com/source") -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Albuquerque Public Schools",
        email="jane.smith@aps.edu",
        email_status="verified_found",
        source_url=source_url,
        confidence=0.9,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed APS is scaling its technology leadership.",
        fit_score=0.9,
        evidence_score=0.8,
        contact_score=0.7,
        gate_passed=True,
        explanation="Strong district fit with current leadership evidence and usable email.",
    )


def test_validate_candidate_source_marks_verified_found_fields_from_page_content():
    candidate = _make_lead()
    client = FakeClient(
        FakeResponse(
            200,
            "Jane Smith is the Director of Technology at Albuquerque Public Schools. "
            "Reach her at jane.smith@aps.edu.",
            "https://aps.edu/leadership/jane-smith",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == [candidate.source_url]
    assert client.follow_redirects == [True]
    assert validation.source.status == "supported"
    assert validation.source.source_url == "https://aps.edu/leadership/jane-smith"
    assert validation.name.status == "supported"
    assert validation.title.status == "supported"
    assert validation.organization.status == "supported"
    assert validation.email.status == "verified_found"
    assert validation.phone.status == "missing"
    assert validation.source.checked_at.endswith("Z")
    assert "http_status=200" in validation.source.notes
    assert "matched_fields=name,title,organization,email" in validation.source.notes


def test_validate_candidate_source_marks_200_without_matches_unsupported():
    candidate = _make_lead(source_url="https://example.com/no-match")
    client = FakeClient(
        FakeResponse(
            200,
            "Example Corp publishes a generic homepage without person-specific details.",
            "https://example.com/home",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert validation.source.status == "unsupported"
    assert validation.source.source_url == "https://example.com/home"
    assert validation.name.status == "unsupported"
    assert validation.title.status == "unsupported"
    assert validation.organization.status == "unsupported"
    assert validation.email.status == "unsupported"
    assert "matched_fields=none" in validation.source.notes


def test_validate_candidate_source_supports_k12_tech_role_family_with_snippet():
    candidate = Lead(
        name="Jon Castelhano",
        title="Executive Director of Technology",
        organization="Gilbert Public Schools",
        email="",
        email_status="missing",
        source_url="https://www.gilbertschools.net/contact",
        confidence=0.8,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed Gilbert Public Schools lists a technology leadership team.",
        fit_score=0.8,
        evidence_score=0.7,
        contact_score=0.0,
        gate_passed=False,
        explanation="Official district contact page lists technology leadership.",
    )
    client = FakeClient(
        FakeResponse(
            200,
            "Contact Us - Gilbert Public Schools. Department Staff Directory. "
            "Technology Jon Castelhano CHIEF TECHNOLOGY OFFICER Donalee McIntyre "
            "EXECUTIVE ASSISTANT Scott Haase DIRECTOR - TECH INFRASTRUCTURE AND CYBERSECURITY.",
            "https://www.gilbertschools.net/contact",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert validation.name.status == "supported"
    assert validation.title.status == "supported"
    assert validation.title.evidence_snippet is not None
    assert "Jon Castelhano" in validation.title.evidence_snippet
    assert "CHIEF TECHNOLOGY OFFICER" in validation.title.evidence_snippet
    assert validation.title.notes == "Role-family text support found for title."
    assert validation.organization.status == "supported"
    assert validation.email.status == "missing"
    assert "matched_fields=name,title,organization" in validation.source.notes


@pytest.mark.parametrize("status_code", [403, 404, 999])
def test_validate_candidate_source_marks_inaccessible_sources_failed(status_code):
    candidate = _make_lead(source_url="https://example.com/blocked")
    client = FakeClient(FakeResponse(status_code, "Access denied", "https://example.com/blocked"))

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert validation.source.status == "failed"
    assert validation.source.source_url == "https://example.com/blocked"
    assert validation.name.status == "failed"
    assert validation.title.status == "failed"
    assert validation.organization.status == "failed"
    assert validation.email.status == "failed"
    assert f"http_status={status_code}" in validation.source.notes


def test_validate_candidate_source_marks_missing_source_without_network():
    candidate = OrganizationOnlyCandidate(
        organization="Example Corp",
        explanation="The account exists, but no validated person was found.",
    )
    client = FakeClient(
        FakeResponse(
            200,
            "This response should never be fetched.",
            "https://example.com/unused",
        )
    )

    validation = asyncio.run(validate_candidate_source(candidate, client=client))

    assert client.requested_urls == []
    assert validation.source.status == "missing"
    assert validation.source.source_url is None
    assert validation.organization.status == "failed"
    assert validation.name.status == "missing"
    assert validation.title.status == "missing"
    assert validation.email.status == "missing"
