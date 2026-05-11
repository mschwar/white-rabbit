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
    assert report.high_noise_count == 2
    assert report.high_noise_rate == 0.4
    assert report.quality_gate_passed is False
    assert report.quality_gate_failures == (
        "low_precision_rate",
        "low_persona_match_rate",
        "low_contact_quality_rate",
        "fake_emails_present",
        "unsupported_emails_present",
    )
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
    assert payload["high_noise_rate"] == 0.4
    assert payload["quality_gate_passed"] is False
    assert "fake_emails_present" in payload["quality_gate_failures"]
    assert payload["quality_gate_thresholds"]["minimum_precision_rate"] == 0.5
    assert payload["candidate_category_counts"]["not_found"] == 1
    assert payload["validation_status_counts"]["email"]["failed"] == 1


def test_quality_report_reports_ready_blockers_for_non_crm_ready_rows():
    missing_contact = _lead(
        email_status="missing",
        validation=_validation(email_status="missing"),
        gate_passed=False,
    )
    missing_contact.tier = "review"
    missing_contact.primary_filter_reason = "REVIEW: contact is missing; row is not CRM-ready."

    unsupported_pattern = _lead(
        email_status="unsupported",
        validation=_validation(email_status="unsupported"),
        gate_passed=False,
    )
    unsupported_pattern.tier = "review"
    unsupported_pattern.primary_filter_reason = "REVIEW: contact is unsupported; row is not CRM-ready."

    unsupported_title = _lead(
        email_status="verified_found",
        validation=_validation(title_status="unsupported", email_status="verified_found"),
        gate_passed=False,
    )
    unsupported_title.tier = "review"
    unsupported_title.primary_filter_reason = "REVIEW: name, title, or organization lacks direct source support."

    report = build_quality_report(
        [
            missing_contact,
            unsupported_pattern,
            unsupported_title,
            _organization_only(),
        ],
        artifact_kind="benchmark",
        artifact_id="ready-blocker-check",
        query="operations leaders in Austin",
    )

    assert report.ready_blocker_counts == {
        "no_contact_source": 1,
        "no_validated_domain_pattern": 1,
        "title_unsupported": 1,
        "organization_only": 1,
    }
    assert [entry["blocker"] for entry in report.candidate_ready_blockers] == [
        "no_contact_source",
        "no_validated_domain_pattern",
        "title_unsupported",
        "organization_only",
    ]
    assert report.to_payload()["candidate_ready_blockers"][0]["reason"].startswith("REVIEW:")


def test_quality_report_passes_clean_runs_against_default_gate_thresholds():
    report = build_quality_report(
        [
            _lead(email_status="verified_found"),
            _lead(
                email_status="deduced_with_pattern_evidence",
                validation=_validation(email_status="deduced_with_pattern_evidence"),
            ),
        ],
        artifact_kind="run",
        artifact_id="run-clean",
        query="K-12 IT directors in Arizona",
    )

    assert report.precision_rate == 1.0
    assert report.high_noise_count == 0
    assert report.high_noise_rate == 0.0
    assert report.quality_gate_passed is True
    assert report.quality_gate_failures == ()


def test_quality_report_fails_zero_usable_runs():
    report = build_quality_report(
        [_organization_only(), _not_found(), _failed()],
        artifact_kind="run",
        artifact_id="run-zero-usable",
        query="K-12 IT directors in Arizona",
    )

    assert report.usable_count == 0
    assert report.quality_gate_passed is False
    assert "zero_usable_candidates" in report.quality_gate_failures


def test_quality_report_fails_high_noise_runs():
    report = build_quality_report(
        [
            _lead(email_status="verified_found"),
            _organization_only(),
            _failed(),
        ],
        artifact_kind="run",
        artifact_id="run-high-noise",
        query="K-12 IT directors in Arizona",
        quality_gate_thresholds={
            "minimum_precision_rate": 0.3,
            "minimum_persona_match_rate": 0.3,
            "minimum_contact_quality_rate": 0.3,
            "minimum_source_support_rate": 0.3,
        },
    )

    assert report.high_noise_count == 2
    assert report.high_noise_rate == 0.667
    assert report.quality_gate_passed is False
    assert "high_noise_rate" in report.quality_gate_failures
