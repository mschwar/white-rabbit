from __future__ import annotations

from core.coverage import write_nonperson_coverage
from core.models import Lead, NotFoundCandidate, OrganizationOnlyCandidate
from core.query_planner import QueryPlan
from core.source_collection import CollectedSource, SourceCollectionSnapshot


def _query_plan() -> QueryPlan:
    return QueryPlan(
        original_query="Mesa and Ghost District technology leaders",
        vendor_queries=[
            "Mesa Public Schools technology leaders",
            "Ghost District technology leaders",
        ],
        named_accounts=["Mesa Public Schools", "Ghost District"],
        intent_summary="technology leaders",
        target_raw_results=20,
    )


def _source_collection() -> SourceCollectionSnapshot:
    return SourceCollectionSnapshot(
        query="Mesa and Ghost District technology leaders",
        collected_at="2026-05-11T00:00:00Z",
        requested_max_results=20,
        returned_source_count=1,
        tavily_searches=2,
        search_depth="advanced",
        query_plan=None,
        sources=[
            CollectedSource(
                source_id="src_mesa",
                rank=1,
                title="Mesa Public Schools technology department",
                url="https://www.mpsaz.org/technology",
                content="Mesa Public Schools lists district technology services.",
                score=0.91,
                vendor_query="Mesa Public Schools technology leaders",
                matched_vendor_queries=["Mesa Public Schools technology leaders"],
                content_sha256="abc123",
            )
        ],
    )


def _lead() -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Mesa Public Schools",
        email="jane.smith@mpsaz.org",
        email_status="verified_found",
        source_url="https://www.mpsaz.org/technology",
        confidence=0.9,
        why_target="Technology leader at a named target district.",
        icebreaker="I saw your technology team supports Mesa Public Schools.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.9,
        gate_passed=True,
        explanation="Strong fit for the named account.",
    )


def test_write_nonperson_coverage_adds_organization_only_and_not_found_rows():
    candidates = write_nonperson_coverage(
        [],
        query_plan=_query_plan(),
        source_collection=_source_collection(),
    )

    assert [candidate.candidate_category for candidate in candidates] == [
        "organization_only",
        "not_found",
    ]
    assert isinstance(candidates[0], OrganizationOnlyCandidate)
    assert candidates[0].organization == "Mesa Public Schools"
    assert candidates[0].source_url == "https://www.mpsaz.org/technology"
    assert "no usable person lead was validated" in candidates[0].explanation
    assert isinstance(candidates[1], NotFoundCandidate)
    assert candidates[1].searched_target == "Ghost District"
    assert "named-account obligation" in candidates[1].explanation


def test_write_nonperson_coverage_does_not_duplicate_existing_account_rows():
    candidates = write_nonperson_coverage(
        [_lead()],
        query_plan=_query_plan(),
        source_collection=_source_collection(),
    )

    assert [candidate.candidate_category for candidate in candidates] == [
        "person_lead",
        "not_found",
    ]
    assert candidates[0].organization == "Mesa Public Schools"
    assert candidates[1].searched_target == "Ghost District"


def test_write_nonperson_coverage_ignores_broad_queries_without_named_accounts():
    plan = QueryPlan(
        original_query="healthcare IT directors in Phoenix",
        vendor_queries=["healthcare IT directors in Phoenix"],
        named_accounts=[],
        broad_query=True,
    )

    assert write_nonperson_coverage([_lead()], query_plan=plan, source_collection=None) == [_lead()]
