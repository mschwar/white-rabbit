from core.models import CandidateValidation, ContactValidationRecord, FieldValidationRecord, Lead
from core.sampled_precision import build_sampled_precision_packet


def _field(status: str = "supported") -> FieldValidationRecord:
    return FieldValidationRecord(
        status=status,
        source_url="https://district.example.edu/staff",
        evidence_snippet=f"{status} evidence",
        checked_at="2026-05-24T12:00:00Z",
        notes=f"{status} notes",
    )


def _contact(status: str = "verified_found") -> ContactValidationRecord:
    return ContactValidationRecord(
        status=status,
        source_url="https://district.example.edu/staff",
        evidence_snippet=f"{status} contact",
        checked_at="2026-05-24T12:00:00Z",
        notes=f"{status} notes",
    )


def _lead(name: str, *, email_status: str = "verified_found", title_status: str = "supported") -> Lead:
    return Lead(
        name=name,
        title="Director of Technology",
        organization="Mesa Public Schools",
        email=f"{name.lower().replace(' ', '.')}@mpsaz.org" if email_status == "verified_found" else "",
        email_status=email_status,
        source_url="https://www.mpsaz.org/technology",
        confidence=0.9,
        why_target="District technology decision maker.",
        icebreaker="I saw your technology work at Mesa Public Schools.",
        fit_score=0.9,
        evidence_score=0.9,
        contact_score=0.9 if email_status == "verified_found" else 0.1,
        gate_passed=email_status == "verified_found" and title_status == "supported",
        explanation="Source-backed district technology lead.",
        validation=CandidateValidation(
            name=_field(),
            title=_field(title_status),
            organization=_field(),
            email=_contact(email_status),
            phone=_contact("missing"),
            source=_field(),
        ),
    )


def test_sampled_precision_packet_is_deterministic_and_counts_support_dimensions():
    unsupported_email_lead = _lead("Maria Garcia", email_status="unsupported")
    unsupported_email_lead.email = "maria.garcia@example.test"
    packet = build_sampled_precision_packet(
        {
            "thomas-arizona-k12": [
                _lead("Jane Smith"),
                unsupported_email_lead,
                _lead("Alex Johnson", title_status="unsupported"),
            ]
        },
        sample_size_per_case=3,
    )

    assert packet.sampled_row_count == 3
    assert [row.row_index for row in packet.rows] == [0, 1, 2]
    assert packet.persona_precision == 0.667
    assert packet.organization_precision == 1.0
    assert packet.source_support_precision == 1.0
    assert packet.contact_support_precision == 0.667
    assert packet.unsupported_email_count == 1
    assert packet.fake_email_count == 0
    assert packet.green_precision_floor_met is False


def test_sampled_precision_does_not_count_redacted_empty_email_as_unsupported_contact():
    lead = _lead("Brian Boone", email_status="unsupported")
    lead.email = ""

    packet = build_sampled_precision_packet({"thomas-arizona-k12": [lead]})

    assert packet.sampled_row_count == 1
    assert packet.contact_support_precision == 0.0
    assert packet.unsupported_email_count == 0
