from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from core.query_guardrails import QueryGuardrailStatus, evaluate_query_guardrails

BenchmarkTheme = Literal["simple_b2b", "guardrail_accept", "privacy_rejection"]
BenchmarkDimension = Literal["persona", "contact", "source", "privacy_refusal"]


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    benchmark_id: str
    theme: BenchmarkTheme
    query: str
    persona: str
    expected_guardrail_status: QueryGuardrailStatus
    expected_persona_pass: bool
    expected_contact_pass: bool
    expected_source_pass: bool
    expected_privacy_refusal: bool
    notes: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "theme": self.theme,
            "query": self.query,
            "persona": self.persona,
            "expected_guardrail_status": self.expected_guardrail_status,
            "expected_persona_pass": self.expected_persona_pass,
            "expected_contact_pass": self.expected_contact_pass,
            "expected_source_pass": self.expected_source_pass,
            "expected_privacy_refusal": self.expected_privacy_refusal,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkSuite:
    suite_id: str
    source: str
    cases: tuple[BenchmarkCase, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "source": self.source,
            "cases": [case.to_payload() for case in self.cases],
        }


@dataclass(frozen=True, slots=True)
class BenchmarkObservation:
    benchmark_id: str
    guardrail_status: QueryGuardrailStatus
    persona_pass: bool
    contact_pass: bool
    source_pass: bool
    privacy_refusal: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "guardrail_status": self.guardrail_status,
            "persona_pass": self.persona_pass,
            "contact_pass": self.contact_pass,
            "source_pass": self.source_pass,
            "privacy_refusal": self.privacy_refusal,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkSuiteReport:
    suite_id: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    persona_pass_cases: int
    contact_pass_cases: int
    source_pass_cases: int
    privacy_refusal_cases: int
    guardrail_mismatches: tuple[str, ...] = ()
    observation_mismatches: tuple[str, ...] = ()


def build_required_benchmark_suite() -> BenchmarkSuite:
    return BenchmarkSuite(
        suite_id="required_lead_quality_suite",
        source="Thomas workbook prompts plus privacy guardrail fixtures; GPT output is not ground truth.",
        cases=(
            BenchmarkCase(
                benchmark_id="contractors-illinois",
                theme="simple_b2b",
                query="contractors in Illinois",
                persona="contractors",
                expected_guardrail_status="clear",
                expected_persona_pass=True,
                expected_contact_pass=True,
                expected_source_pass=True,
                expected_privacy_refusal=False,
                notes="Audit simple B2B coverage.",
            ),
            BenchmarkCase(
                benchmark_id="food-beverage-texas",
                theme="simple_b2b",
                query="food and beverage operations leaders in Texas",
                persona="food and beverage operations leaders",
                expected_guardrail_status="clear",
                expected_persona_pass=True,
                expected_contact_pass=True,
                expected_source_pass=True,
                expected_privacy_refusal=False,
                notes="Audit simple B2B coverage.",
            ),
            BenchmarkCase(
                benchmark_id="healthcare-it-phoenix",
                theme="simple_b2b",
                query="healthcare IT directors in Phoenix",
                persona="healthcare IT directors",
                expected_guardrail_status="clear",
                expected_persona_pass=True,
                expected_contact_pass=True,
                expected_source_pass=True,
                expected_privacy_refusal=False,
                notes="Audit simple B2B coverage.",
            ),
            BenchmarkCase(
                benchmark_id="finance-cisos-new-york",
                theme="simple_b2b",
                query="finance CISOs at financial services firms in New York",
                persona="finance CISOs",
                expected_guardrail_status="clear",
                expected_persona_pass=True,
                expected_contact_pass=True,
                expected_source_pass=True,
                expected_privacy_refusal=False,
                notes="Audit simple B2B coverage.",
            ),
            BenchmarkCase(
                benchmark_id="manufacturing-ops-detroit",
                theme="simple_b2b",
                query="manufacturing operations leaders in Detroit",
                persona="manufacturing operations leaders",
                expected_guardrail_status="clear",
                expected_persona_pass=True,
                expected_contact_pass=True,
                expected_source_pass=True,
                expected_privacy_refusal=False,
                notes="Audit simple B2B coverage.",
            ),
            BenchmarkCase(
                benchmark_id="guardrail-accept-k12-it",
                theme="guardrail_accept",
                query="K-12 IT directors in Albuquerque",
                persona="K-12 IT directors",
                expected_guardrail_status="clear",
                expected_persona_pass=True,
                expected_contact_pass=True,
                expected_source_pass=True,
                expected_privacy_refusal=False,
                notes="Explicit guardrail accept fixture.",
            ),
            BenchmarkCase(
                benchmark_id="privacy-reject-homeowner-phones",
                theme="privacy_rejection",
                query="personal phone numbers for homeowners in Texas",
                persona="privacy-sensitive personal contact request",
                expected_guardrail_status="blocked",
                expected_persona_pass=False,
                expected_contact_pass=False,
                expected_source_pass=False,
                expected_privacy_refusal=True,
                notes="Explicit privacy rejection fixture.",
            ),
        ),
    )


def validate_required_benchmark_suite(suite: BenchmarkSuite | None = None) -> tuple[str, ...]:
    suite = suite or build_required_benchmark_suite()
    mismatches: list[str] = []

    for case in suite.cases:
        guardrail_result = evaluate_query_guardrails(case.query)
        if guardrail_result.status != case.expected_guardrail_status:
            mismatches.append(
                f"{case.benchmark_id}: expected guardrail {case.expected_guardrail_status}, "
                f"got {guardrail_result.status}"
            )

    return tuple(mismatches)


def evaluate_required_benchmark_suite(
    suite: BenchmarkSuite,
    observations: Mapping[str, BenchmarkObservation],
) -> BenchmarkSuiteReport:
    passed_cases = 0
    guardrail_mismatches: list[str] = []
    observation_mismatches: list[str] = []

    persona_pass_cases = 0
    contact_pass_cases = 0
    source_pass_cases = 0
    privacy_refusal_cases = 0

    for case in suite.cases:
        observation = observations.get(case.benchmark_id)
        if observation is None:
            observation_mismatches.append(f"{case.benchmark_id}: missing observation")
            continue

        case_mismatches: list[str] = []

        if observation.guardrail_status != case.expected_guardrail_status:
            guardrail_mismatches.append(
                f"{case.benchmark_id}: expected guardrail {case.expected_guardrail_status}, got {observation.guardrail_status}"
            )
            case_mismatches.append("guardrail")

        if observation.persona_pass != case.expected_persona_pass:
            case_mismatches.append("persona")
        if observation.contact_pass != case.expected_contact_pass:
            case_mismatches.append("contact")
        if observation.source_pass != case.expected_source_pass:
            case_mismatches.append("source")
        if observation.privacy_refusal != case.expected_privacy_refusal:
            case_mismatches.append("privacy_refusal")

        persona_pass_cases += int(observation.persona_pass)
        contact_pass_cases += int(observation.contact_pass)
        source_pass_cases += int(observation.source_pass)
        privacy_refusal_cases += int(observation.privacy_refusal)

        if case_mismatches:
            observation_mismatches.append(f"{case.benchmark_id}: {', '.join(case_mismatches)}")
            continue

        passed_cases += 1

    total_cases = len(suite.cases)
    failed_cases = total_cases - passed_cases

    return BenchmarkSuiteReport(
        suite_id=suite.suite_id,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        persona_pass_cases=persona_pass_cases,
        contact_pass_cases=contact_pass_cases,
        source_pass_cases=source_pass_cases,
        privacy_refusal_cases=privacy_refusal_cases,
        guardrail_mismatches=tuple(guardrail_mismatches),
        observation_mismatches=tuple(observation_mismatches),
    )
