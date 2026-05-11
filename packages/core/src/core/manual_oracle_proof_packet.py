from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .manual_oracle import CRM_READY_CONTACT_STATUSES, evaluate_manual_oracle_replay
from .research_workbook import (
    ResearchWorkbookSummary,
    build_april_nm_research_workbook_replay,
)
from .source_assisted_compiler import SourceAssistedCompileSummary


_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_R09H_ARTIFACT_DIR = _REPO_ROOT / "audits/raw/reset-2026-05-10/r09h"
DEFAULT_R09H_PACKET_JSON_PATH = DEFAULT_R09H_ARTIFACT_DIR / "manual-oracle-proof-packet.json"
DEFAULT_R09H_PACKET_MARKDOWN_PATH = DEFAULT_R09H_ARTIFACT_DIR / "manual-oracle-proof-packet.md"
DEFAULT_R09H_GENERATED_AT = "2026-05-11T00:00:00Z"


@dataclass(frozen=True, slots=True)
class ManualOracleProofPacket:
    packet_id: str
    feature_id: str
    generated_at: str
    manual_oracle_replay: Mapping[str, Any]
    source_assisted_replay: Mapping[str, Any]
    workbook_replay: Mapping[str, Any]
    safety_checks: Mapping[str, Any]
    live_source_assisted_status: Mapping[str, Any]
    rg3_recommendation: str
    prompt_c_handoff: Mapping[str, Any]

    def passes(self) -> bool:
        return (
            bool(self.manual_oracle_replay.get("structure_reproduced"))
            and bool(self.source_assisted_replay.get("passes"))
            and bool(self.workbook_replay.get("passes"))
            and bool(self.safety_checks.get("passes"))
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "feature_id": self.feature_id,
            "generated_at": self.generated_at,
            "manual_oracle_replay": dict(self.manual_oracle_replay),
            "source_assisted_replay": dict(self.source_assisted_replay),
            "workbook_replay": dict(self.workbook_replay),
            "safety_checks": dict(self.safety_checks),
            "live_source_assisted_status": dict(self.live_source_assisted_status),
            "rg3_recommendation": self.rg3_recommendation,
            "prompt_c_handoff": dict(self.prompt_c_handoff),
            "passes": self.passes(),
        }

    def to_markdown(self) -> str:
        tier_distribution = dict(self.workbook_replay.get("tier_distribution", {}))
        live_status = dict(self.live_source_assisted_status)
        lines = [
            "# R09H Manual-Oracle Proof Replay Gate Packet",
            "",
            f"**Feature:** {self.feature_id}",
            f"**Generated at:** {self.generated_at}",
            f"**Packet pass:** {'yes' if self.passes() else 'no'}",
            f"**RG3 recommendation:** {self.rg3_recommendation}",
            "",
            "## Source-Assisted Replay",
            "",
            f"- Manual-oracle structure reproduced: {_yes_no(self.manual_oracle_replay.get('structure_reproduced'))}",
            f"- Observed rows: {self.manual_oracle_replay.get('observed_rows')} of {self.manual_oracle_replay.get('expected_rows')}",
            f"- Verified-contact rows: {self.manual_oracle_replay.get('verified_contact_rows')}",
            f"- Manual-lookup rows: {self.manual_oracle_replay.get('manual_lookup_rows')}",
            f"- Source-assisted compiler rows: {self.source_assisted_replay.get('candidate_count')}",
            f"- Compiler blocked generic source URLs: {len(self.source_assisted_replay.get('blocked_source_urls', []))}",
            "",
            "## Workbook Proof",
            "",
            f"- Workbook rows: {self.workbook_replay.get('row_count')}",
            f"- READY_WITH_CONTACT: {tier_distribution.get('READY_WITH_CONTACT', 0)}",
            f"- MANUAL_LOOKUP: {tier_distribution.get('MANUAL_LOOKUP', 0)}",
            f"- Downgraded ready rows: {len(self.workbook_replay.get('downgraded_ready_rows', []))}",
            f"- Unsupported CRM-ready contacts: {len(self.safety_checks.get('unsupported_crm_ready_rows', []))}",
            f"- Manual-lookup CRM-ready rows: {len(self.safety_checks.get('manual_lookup_crm_ready_rows', []))}",
            "",
            "## Live/Source-Assisted Status",
            "",
            f"- Credentials present: {_yes_no(live_status.get('credentials_present'))}",
            f"- API health checked: {_yes_no(live_status.get('api_health_checked'))}",
            f"- API health status: {live_status.get('api_health_status', 'not_checked')}",
            f"- Fresh live benchmark run: {_yes_no(live_status.get('fresh_live_benchmark_run'))}",
            f"- Latest saved live high-trust usable rows: {live_status.get('latest_saved_live_high_trust_usable_rows')}",
            f"- Latest saved live contact-quality passes: {live_status.get('latest_saved_live_contact_quality_passes')}",
            "",
            "## Prompt C Handoff",
            "",
            f"- Ready after Prompt B merge: {_yes_no(self.prompt_c_handoff.get('ready_after_prompt_b_merge'))}",
            f"- Required branch: {self.prompt_c_handoff.get('integration_branch')}",
            f"- Required report: {self.prompt_c_handoff.get('required_report')}",
            f"- Keep downstream blocked: {_yes_no(self.prompt_c_handoff.get('keep_downstream_blocked'))}",
            "",
        ]
        return "\n".join(lines)


def build_manual_oracle_proof_packet(
    *,
    workbook_summary: ResearchWorkbookSummary | None = None,
    live_quality_summary: Mapping[str, Any] | None = None,
    live_service_status: Mapping[str, Any] | None = None,
    generated_at: str = DEFAULT_R09H_GENERATED_AT,
) -> ManualOracleProofPacket:
    workbook_summary = workbook_summary or build_april_nm_research_workbook_replay(
        run_id="r09h-april-nm-manual-oracle-proof"
    )
    compiler_summary = _compiler_summary_from_workbook(workbook_summary)
    workbook_payload = workbook_summary.to_payload()
    source_payload = compiler_summary.to_payload()
    manual_payload = evaluate_manual_oracle_replay(compiler_summary.candidate_payloads).to_payload()
    safety_checks = _build_safety_checks(workbook_summary)
    live_status = _build_live_source_assisted_status(
        live_quality_summary=live_quality_summary,
        live_service_status=live_service_status,
    )

    return ManualOracleProofPacket(
        packet_id="r09h_manual_oracle_proof_replay_gate_packet",
        feature_id="R09H - Manual-oracle proof replay gate packet",
        generated_at=generated_at,
        manual_oracle_replay=manual_payload,
        source_assisted_replay=_source_assisted_summary_payload(source_payload),
        workbook_replay=_workbook_summary_payload(workbook_payload),
        safety_checks=safety_checks,
        live_source_assisted_status=live_status,
        rg3_recommendation=_recommend_rg3(manual_payload, source_payload, workbook_payload, safety_checks, live_status),
        prompt_c_handoff={
            "ready_after_prompt_b_merge": True,
            "integration_branch": "rebuild/validated-leads-loop",
            "required_report": "audits/gates/reset-2026-05-10/rg3-validation-semantics.md",
            "required_action": "After R09H passes QA and merges, run Prompt C for RG3 from current integration-branch state.",
            "keep_downstream_blocked": True,
            "blocked_scope": [
                "RG4",
                "refreshed mockups",
                "R10-R12",
                "export work",
                "dogfood",
                "main promotion",
            ],
        },
    )


def write_r09h_proof_packet_artifacts(
    output_dir: Path | None = None,
    *,
    packet: ManualOracleProofPacket | None = None,
    live_quality_summary: Mapping[str, Any] | None = None,
    live_service_status: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    artifact_dir = output_dir or DEFAULT_R09H_ARTIFACT_DIR
    artifact_dir.mkdir(parents=True, exist_ok=True)
    proof_packet = packet or build_manual_oracle_proof_packet(
        live_quality_summary=live_quality_summary,
        live_service_status=live_service_status,
    )

    json_path = artifact_dir / DEFAULT_R09H_PACKET_JSON_PATH.name
    markdown_path = artifact_dir / DEFAULT_R09H_PACKET_MARKDOWN_PATH.name
    json_path.write_text(
        json.dumps(proof_packet.to_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(proof_packet.to_markdown().rstrip() + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def _compiler_summary_from_workbook(summary: ResearchWorkbookSummary) -> SourceAssistedCompileSummary:
    from .source_assisted_compiler import compile_april_nm_source_assisted_replay

    source_summary = compile_april_nm_source_assisted_replay()
    if source_summary.compiler_id != summary.source_compiler_id:
        return source_summary
    return source_summary


def _build_safety_checks(summary: ResearchWorkbookSummary) -> dict[str, Any]:
    unsupported_crm_ready_rows = []
    manual_lookup_crm_ready_rows = []
    missing_source_rows = []
    missing_next_action_rows = []

    for row in summary.rows:
        if row.crm_ready and row.email_status not in CRM_READY_CONTACT_STATUSES:
            unsupported_crm_ready_rows.append(row.candidate_id or row.organization)
        if row.workbook_tier == "MANUAL_LOOKUP":
            if row.crm_ready:
                manual_lookup_crm_ready_rows.append(row.candidate_id or row.organization)
            if not row.next_action:
                missing_next_action_rows.append(row.candidate_id or row.organization)
        if not (
            row.source_name_url
            or row.source_title_url
            or row.source_org_url
            or row.source_email_url
            or row.source_phone_url
        ):
            missing_source_rows.append(row.candidate_id or row.organization)

    return {
        "unsupported_crm_ready_rows": unsupported_crm_ready_rows,
        "manual_lookup_crm_ready_rows": manual_lookup_crm_ready_rows,
        "missing_source_rows": missing_source_rows,
        "missing_next_action_rows": missing_next_action_rows,
        "private_contact_values_redacted": all("@" not in row.email for row in summary.rows),
        "passes": not (
            unsupported_crm_ready_rows
            or manual_lookup_crm_ready_rows
            or missing_source_rows
            or missing_next_action_rows
        ),
    }


def _build_live_source_assisted_status(
    *,
    live_quality_summary: Mapping[str, Any] | None,
    live_service_status: Mapping[str, Any] | None,
) -> dict[str, Any]:
    status = {
        "credentials_present": None,
        "api_health_checked": False,
        "api_health_status": "not_checked",
        "fresh_live_benchmark_run": False,
        "fresh_live_benchmark_reason": (
            "R09H Prompt A built the replay packet; the full live RG3 suite belongs to Prompt C "
            "after R09H passes QA and merges."
        ),
        "latest_saved_live_high_trust_usable_rows": None,
        "latest_saved_live_contact_quality_passes": None,
        "latest_saved_live_summary_source": "",
    }
    if live_service_status:
        status.update(dict(live_service_status))

    if live_quality_summary:
        live_counts = _live_counts(live_quality_summary)
        status.update(
            {
                "latest_saved_live_high_trust_usable_rows": live_counts["high_trust_usable_rows"],
                "latest_saved_live_contact_quality_passes": live_counts["contact_quality_passes"],
                "latest_saved_live_summary_source": str(
                    live_quality_summary.get("artifact_path", "provided_live_quality_summary")
                ),
            }
        )
    return status


def _live_counts(summary: Mapping[str, Any]) -> dict[str, int]:
    high_trust = 0
    contact_passes = 0
    for case_summary in dict(summary.get("case_summaries", {})).values():
        if not isinstance(case_summary, Mapping):
            continue
        high_trust += _int(case_summary.get("high_trust_usable_count"))
        funnel_counts = case_summary.get("funnel_counts")
        if isinstance(funnel_counts, Mapping) and "contact_quality_passes" in funnel_counts:
            contact_passes += _int(funnel_counts.get("contact_quality_passes"))
            continue
        quality_report = case_summary.get("quality_report")
        if isinstance(quality_report, Mapping):
            contact_passes += _int(quality_report.get("contact_quality_count"))
    return {
        "high_trust_usable_rows": high_trust,
        "contact_quality_passes": contact_passes,
    }


def _source_assisted_summary_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    manual_replay = dict(payload.get("manual_oracle_replay") or {})
    return {
        "compiler_id": payload.get("compiler_id"),
        "candidate_count": payload.get("candidate_count"),
        "source_count": payload.get("source_count"),
        "tier_distribution": dict(payload.get("tier_distribution") or {}),
        "blocked_source_urls": list(payload.get("blocked_source_urls") or []),
        "manual_oracle_replay": {
            "structure_reproduced": manual_replay.get("structure_reproduced"),
            "verified_contact_rows": manual_replay.get("verified_contact_rows"),
            "manual_lookup_rows": manual_replay.get("manual_lookup_rows"),
            "unsupported_ready_contacts": list(manual_replay.get("unsupported_ready_contacts") or []),
        },
        "passes": payload.get("passes"),
    }


def _workbook_summary_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "workbook_id": payload.get("workbook_id"),
        "source_compiler_id": payload.get("source_compiler_id"),
        "row_count": payload.get("row_count"),
        "source_count": payload.get("source_count"),
        "tier_distribution": dict(payload.get("tier_distribution") or {}),
        "export_headers": list(payload.get("export_headers") or []),
        "downgraded_ready_rows": list(payload.get("downgraded_ready_rows") or []),
        "passes": payload.get("passes"),
    }


def _recommend_rg3(
    manual_payload: Mapping[str, Any],
    source_payload: Mapping[str, Any],
    workbook_payload: Mapping[str, Any],
    safety_checks: Mapping[str, Any],
    live_status: Mapping[str, Any],
) -> str:
    replay_passes = (
        bool(manual_payload.get("structure_reproduced"))
        and bool(source_payload.get("passes"))
        and bool(workbook_payload.get("passes"))
        and bool(safety_checks.get("passes"))
    )
    if not replay_passes:
        return "hold: source-assisted manual-oracle proof packet failed replay safety checks"

    live_high_trust = live_status.get("latest_saved_live_high_trust_usable_rows")
    live_contact_passes = live_status.get("latest_saved_live_contact_quality_passes")
    if live_high_trust == 0 or live_contact_passes == 0:
        return (
            "hold_pending_prompt_c_live_audit: source-assisted replay passes, but latest saved live "
            "benchmark evidence still has zero high-trust/contact-quality output"
        )

    return (
        "prompt_c_ready: source-assisted replay passes; future Prompt C must rerun RG3 live evidence "
        "before any gate advance"
    )


def _int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"
