from core.models import (
    CandidateValidation,
    ContactValidationRecord,
    FailedCandidate,
    FieldValidationRecord,
    Lead,
    NotFoundCandidate,
    OrganizationOnlyCandidate,
)
from core.quality_report import build_quality_report


def _field(status: str = "supported") -> FieldValidationRecord:
    return FieldValidationRecord(
        status=status,
        source_url="https://example.com/source",
        evidence_snippet=f"test {status}",
        checked_at="2026-05-10T12:00:00Z",
        notes=f"test {status}",
    )


def _contact(status: str = "verified_found") -> ContactValidationRecord:
    return ContactValidationRecord(
        status=status,
        source_url="https://example.com/contact",
        evidence_snippet=f"test {status}",
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
    phone_status: str = "missing",
) -> CandidateValidation:
    return CandidateValidation(
        name=_field(name_status),
        title=_field(title_status),
        organization=_field(organization_status),
        email=_contact(email_status),
        phone=_contact(phone_status),
        source=_field(source_status),
    )


def _lead(*, email_status: str, validation: CandidateValidation | None = None, gate_passed: bool = True) -> Lead:
    return Lead(
        name="Jane Smith",
        title="Director of Technology",
        organization="Albuquerque Public Schools",
        email="jane.smith@aps.edu" if email_status != "missing" else "",
        email_status=email_status,
        source_url="https://aps.edu/tech",
        confidence=0.9,
        why_target="Fits the district technology ICP.",
        icebreaker="I noticed APS is scaling its technology leadership.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.9,
        gate_passed=gate_passed,
        explanation="Strong district fit with current leadership evidence and usable email.",
        validation=validation or _validation(email_status=email_status),
    )


def _organization_only(*, email_status: str = "unsupported") -> OrganizationOnlyCandidate:
    return OrganizationOnlyCandidate(
        organization="Example Corp",
        explanation="Organization found, but no usable person was validated.",
        validation=_validation(
            name_status="unsupported",
            title_status="unsupported",
            organization_status="supported",
            email_status=email_status,
            source_status="supported",
        ),
    )


def _not_found(*, email_status: str = "missing") -> NotFoundCandidate:
    return NotFoundCandidate(
        searched_target="Example Corp IT director",
        organization="Example Corp",
        explanation="No acceptable contact was found for the target account.",
        validation=_validation(
            name_status="unsupported",
            title_status="unsupported",
            organization_status="unsupported",
            email_status=email_status,
            source_status="supported",
        ),
    )


def _failed(*, email_status: str = "failed") -> FailedCandidate:
    return FailedCandidate(
        searched_target="Example Corp IT director",
        failure_reason="Source was inaccessible.",
        explanation="The candidate could not be trusted.",
        validation=_validation(
            name_status="unsupported",
            title_status="unsupported",
            organization_status="unsupported",
            email_status=email_status,
            source_status="failed",
        ),
    )


def _mixed_candidates() -> list[Lead | OrganizationOnlyCandidate | NotFoundCandidate | FailedCandidate]:
    return [
        _lead(email_status="verified_found"),
        _lead(
            email_status="deduced_with_pattern_evidence",
            validation=_validation(email_status="deduced_with_pattern_evidence"),
        ),
        _organization_only(),
        _not_found(),
        _failed(),
    ]


def test_quality_report_counts_candidate_categories_and_validation_statuses():
    report = build_quality_report(
        _mixed_candidates(),
        artifact_kind="run",
        artifact_id="run-123",
        query="finance CISOs in New York",
    )

    assert report.artifact_kind == "run"
    assert report.artifact_id == "run-123"
    assert report.query == "finance CISOs in New York"
    assert report.total_candidates == 5
    assert report.usable_count == 2
    assert report.precision_rate == 0.4
    assert report.person_lead_count == 2
    assert report.organization_only_count == 1
    assert report.not_found_count == 1
    assert report.failed_count == 1
    assert report.persona_match_count == 2
    assert report.persona_match_rate == 0.4
    assert report.contact_quality_count == 2
    assert report.contact_quality_rate == 0.4
    assert report.source_support_count == 4
    assert report.source_support_rate == 0.8
    assert report.fake_email_count == 1
    assert report.unsupported_email_count == 1
    assert report.candidate_category_counts == {
        "person_lead": 2,
        "organization_only": 1,
        "not_found": 1,
        "failed": 1,
    }
    assert report.validation_status_counts["name"] == {
        "supported": 2,
        "unsupported": 3,
        "missing": 0,
        "failed": 0,
    }
    assert report.validation_status_counts["source"] == {
        "supported": 4,
        "unsupported": 0,
        "missing": 0,
        "failed": 1,
    }
    assert report.validation_status_counts["email"] == {
        "verified_found": 1,
        "deduced_with_pattern_evidence": 1,
        "missing": 1,
        "failed": 1,
        "unsupported": 1,
    }


def test_quality_report_serializes_for_benchmark_artifacts():
    report = build_quality_report(
        _mixed_candidates(),
        artifact_kind="benchmark",
        artifact_id="required_lead_quality_suite",
        query="benchmark quality check",
    )

    payload = report.to_payload()

    assert payload["artifact_kind"] == "benchmark"
    assert payload["artifact_id"] == "required_lead_quality_suite"
    assert payload["query"] == "benchmark quality check"
    assert payload["precision_rate"] == 0.4
    assert payload["fake_email_count"] == 1
    assert payload["candidate_category_counts"]["not_found"] == 1
    assert payload["validation_status_counts"]["email"]["failed"] == 1
