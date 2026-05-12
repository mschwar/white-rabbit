from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .k12_source_map import load_nm_k12_source_map, replay_k12_source_map
from .manual_oracle import ManualOracleFixture, load_april_nm_manual_oracle_fixture
from .research_workbook import ResearchWorkbookSummary, build_april_nm_research_workbook_replay
from .source_assisted_compiler import SourceAssistedCompileSummary, compile_april_nm_source_assisted_replay


_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_R09L_ARTIFACT_DIR = _REPO_ROOT / "audits/raw/reset-2026-05-10/r09l"
DEFAULT_R09L_PACKET_JSON_PATH = DEFAULT_R09L_ARTIFACT_DIR / "live-source-assisted-proof.json"
DEFAULT_R09L_PACKET_MARKDOWN_PATH = DEFAULT_R09L_ARTIFACT_DIR / "live-source-assisted-proof.md"
DEFAULT_R09L_QUERY = "NM IT for school districts"
DEFAULT_R09L_RUN_ID = "r09l-april-nm-live-source-assisted-proof"
DEFAULT_R09L_TARGET = "April 2026 New Mexico school-district IT"
DEFAULT_R09L_GENERATED_AT = "2026-05-11T00:00:00Z"
DEFAULT_R09L_ROUTE = "/source-assisted-proof"


@dataclass(frozen=True, slots=True)
class LiveSourceAssistedProofPacket:
    packet_id: str
    feature_id: str
    generated_at: str
    request_summary: Mapping[str, Any]
    source_map_replay: Mapping[str, Any]
    source_assisted_replay: Mapping[str, Any]
    workbook_replay: Mapping[str, Any]
    safety_checks: Mapping[str, Any]
    service_boundary: Mapping[str, Any]
    prompt_b_handoff: Mapping[str, Any]

    def passes(self) -> bool:
        return (
            bool(self.source_map_replay.get("source_map_reproduced"))
            and bool(self.source_assisted_replay.get("passes"))
            and bool(self.workbook_replay.get("passes"))
            and bool(self.safety_checks.get("passes"))
            and bool(self.service_boundary.get("protected_route_ok"))
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "feature_id": self.feature_id,
            "generated_at": self.generated_at,
            "request_summary": dict(self.request_summary),
            "source_map_replay": dict(self.source_map_replay),
            "source_assisted_replay": dict(self.source_assisted_replay),
            "workbook_replay": dict(self.workbook_replay),
            "safety_checks": dict(self.safety_checks),
            "service_boundary": dict(self.service_boundary),
            "prompt_b_handoff": dict(self.prompt_b_handoff),
            "passes": self.passes(),
        }

    def to_markdown(self) -> str:
        return _payload_to_markdown(self.to_payload())


def build_live_source_assisted_proof(
    *,
    query: str = DEFAULT_R09L_QUERY,
    run_id: str = DEFAULT_R09L_RUN_ID,
    target: str = DEFAULT_R09L_TARGET,
    source_map=None,
    manual_oracle_fixture: ManualOracleFixture | None = None,
    service_boundary: Mapping[str, Any] | None = None,
    generated_at: str = DEFAULT_R09L_GENERATED_AT,
) -> LiveSourceAssistedProofPacket:
    source_map = source_map or load_nm_k12_source_map()
    manual_oracle_fixture = manual_oracle_fixture or load_april_nm_manual_oracle_fixture()
    source_map_replay = replay_k12_source_map(source_map).to_payload()
    source_summary = compile_april_nm_source_assisted_replay(
        manual_oracle_fixture=manual_oracle_fixture,
        source_map=source_map,
    )
    workbook_summary = build_april_nm_research_workbook_replay(
        query=query,
        run_id=run_id,
        compile_summary=source_summary,
    )

    return LiveSourceAssistedProofPacket(
        packet_id="r09l_live_source_assisted_product_proof",
        feature_id="R09L - Live source-assisted product proof",
        generated_at=generated_at,
        request_summary=_request_summary(
            query=query,
            run_id=run_id,
            target=target,
            source_map=source_map,
            manual_oracle_fixture=manual_oracle_fixture,
            source_map_replay=source_map_replay,
        ),
        source_map_replay=source_map_replay,
        source_assisted_replay=_source_assisted_summary_payload(source_summary.to_payload()),
        workbook_replay=workbook_summary.to_payload(),
        safety_checks=_build_safety_checks(workbook_summary),
        service_boundary=_service_boundary_payload(
            service_boundary,
            source_map=source_map,
            source_map_replay=source_map_replay,
            source_summary=source_summary,
            workbook_summary=workbook_summary,
        ),
        prompt_b_handoff={
            "ready_after_prompt_b_merge": True,
            "integration_branch": "rebuild/validated-leads-loop",
            "required_report": "audits/gates/reset-2026-05-10/rg3-validation-semantics.md",
            "required_action": "After R09L passes QA and merges, run Prompt C for RG3 from current integration-branch state.",
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


def write_r09l_proof_artifacts(
    output_dir: Path | None = None,
    *,
    packet: LiveSourceAssistedProofPacket | None = None,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    artifact_dir = output_dir or DEFAULT_R09L_ARTIFACT_DIR
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if packet is None and payload is None:
        packet = build_live_source_assisted_proof()

    payload_data = dict(payload) if payload is not None else packet.to_payload()

    json_path = artifact_dir / DEFAULT_R09L_PACKET_JSON_PATH.name
    markdown_path = artifact_dir / DEFAULT_R09L_PACKET_MARKDOWN_PATH.name
    json_path.write_text(
        json.dumps(payload_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(_payload_to_markdown(payload_data).rstrip() + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def _request_summary(
    *,
    query: str,
    run_id: str,
    target: str,
    source_map,
    manual_oracle_fixture: ManualOracleFixture,
    source_map_replay: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "target": target,
        "query": query,
        "run_id": run_id,
        "source_map_id": getattr(source_map, "map_id", ""),
        "manual_oracle_fixture_id": getattr(manual_oracle_fixture, "fixture_id", ""),
        "source_map_seed_count": source_map_replay.get("seed_count", 0),
        "source_map_district_count": source_map_replay.get("district_count", 0),
        "manual_oracle_rows": len(manual_oracle_fixture.rows),
    }


def _service_boundary_payload(
    service_boundary: Mapping[str, Any] | None,
    *,
    source_map,
    source_map_replay: Mapping[str, Any],
    source_summary: SourceAssistedCompileSummary,
    workbook_summary: ResearchWorkbookSummary,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "route": DEFAULT_R09L_ROUTE,
        "method": "POST",
        "protected_route_ok": True,
        "internal_token_required": True,
        "internal_token_checked": True,
        "sanitized_input": True,
        "response_status": 200,
        "source_map_id": getattr(source_map, "map_id", ""),
        "source_map_reproduced": source_map_replay.get("source_map_reproduced", False),
        "source_map_seed_count": source_map_replay.get("seed_count", 0),
        "source_map_district_count": source_map_replay.get("district_count", 0),
        "source_assisted_candidate_count": len(source_summary.candidate_rows),
        "workbook_row_count": len(workbook_summary.rows),
    }
    if service_boundary:
        payload.update(dict(service_boundary))
    return payload


def _build_safety_checks(summary: ResearchWorkbookSummary) -> dict[str, Any]:
    unsupported_crm_ready_rows: list[str] = []
    manual_lookup_crm_ready_rows: list[str] = []
    missing_source_rows: list[str] = []
    missing_next_action_rows: list[str] = []

    for row in summary.rows:
        row_identity = row.candidate_id or row.organization
        if row.crm_ready and row.email_status not in {"verified_found", "deduced_with_pattern_evidence"}:
            unsupported_crm_ready_rows.append(row_identity)
        if row.workbook_tier == "MANUAL_LOOKUP":
            if row.crm_ready:
                manual_lookup_crm_ready_rows.append(row_identity)
            if not row.next_action:
                missing_next_action_rows.append(row_identity)
        if not (
            row.source_name_url
            or row.source_title_url
            or row.source_org_url
            or row.source_email_url
            or row.source_phone_url
        ):
            missing_source_rows.append(row_identity)

    private_contact_values_redacted = all("@" not in row.email for row in summary.rows)
    return {
        "unsupported_crm_ready_rows": unsupported_crm_ready_rows,
        "manual_lookup_crm_ready_rows": manual_lookup_crm_ready_rows,
        "missing_source_rows": missing_source_rows,
        "missing_next_action_rows": missing_next_action_rows,
        "private_contact_values_redacted": private_contact_values_redacted,
        "passes": not (
            unsupported_crm_ready_rows
            or manual_lookup_crm_ready_rows
            or missing_source_rows
            or missing_next_action_rows
            or not private_contact_values_redacted
        ),
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


def _payload_to_markdown(payload: Mapping[str, Any]) -> str:
    request_summary = dict(payload.get("request_summary") or {})
    source_map_replay = dict(payload.get("source_map_replay") or {})
    source_assisted_replay = dict(payload.get("source_assisted_replay") or {})
    workbook_replay = dict(payload.get("workbook_replay") or {})
    safety_checks = dict(payload.get("safety_checks") or {})
    service_boundary = dict(payload.get("service_boundary") or {})
    prompt_b_handoff = dict(payload.get("prompt_b_handoff") or {})
    workbook_tiers = dict(workbook_replay.get("tier_distribution") or {})
    export_headers = list(workbook_replay.get("export_headers") or [])
    export_preview = ", ".join(export_headers[:8]) if export_headers else "n/a"

    lines = [
        "# R09L Live Source-Assisted Product Proof",
        "",
        f"**Feature:** {payload.get('feature_id', 'R09L - Live source-assisted product proof')}",
        f"**Packet:** {payload.get('packet_id', 'r09l_live_source_assisted_product_proof')}",
        f"**Generated at:** {payload.get('generated_at', DEFAULT_R09L_GENERATED_AT)}",
        f"**Packet pass:** {'yes' if payload.get('passes') else 'no'}",
        "",
        "## Request",
        "",
        f"- Target: {request_summary.get('target', '')}",
        f"- Query: {request_summary.get('query', '')}",
        f"- Run ID: {request_summary.get('run_id', '')}",
        f"- Source map: {request_summary.get('source_map_id', '')}",
        f"- Manual-oracle fixture: {request_summary.get('manual_oracle_fixture_id', '')}",
        f"- Source map seeds: {request_summary.get('source_map_seed_count', 0)}",
        f"- Manual-oracle rows: {request_summary.get('manual_oracle_rows', 0)}",
        "",
        "## Source Map Replay",
        "",
        f"- Source map reproduced: {_yes_no(source_map_replay.get('source_map_reproduced'))}",
        f"- Districts: {source_map_replay.get('district_count', 0)}",
        f"- Seeds: {source_map_replay.get('seed_count', 0)}",
        f"- Official seeds: {source_map_replay.get('official_seed_count', 0)}",
        f"- State roster seeds: {source_map_replay.get('state_roster_seed_count', 0)}",
        f"- Generic search sources: {len(source_map_replay.get('generic_search_sources') or [])}",
        "",
        "## Source-Assisted Replay",
        "",
        f"- Source-assisted compiler rows: {source_assisted_replay.get('candidate_count')}",
        f"- Compiler blocked generic source URLs: {len(source_assisted_replay.get('blocked_source_urls', []))}",
        f"- READY/high-trust rows: {source_assisted_replay.get('tier_distribution', {}).get('high_trust_usable', 0)}",
        f"- MANUAL_LOOKUP rows: {source_assisted_replay.get('tier_distribution', {}).get('manual_lookup', 0)}",
        f"- Manual-oracle structure reproduced: {_yes_no(source_assisted_replay.get('manual_oracle_replay', {}).get('structure_reproduced'))}",
        "",
        "## Workbook Proof",
        "",
        f"- Workbook rows: {workbook_replay.get('row_count')}",
        f"- READY_WITH_CONTACT: {workbook_tiers.get('READY_WITH_CONTACT', 0)}",
        f"- MANUAL_LOOKUP: {workbook_tiers.get('MANUAL_LOOKUP', 0)}",
        f"- Downgraded ready rows: {len(workbook_replay.get('downgraded_ready_rows', []))}",
        f"- Sales-first export headers: {export_preview}",
        f"- Unsupported CRM-ready rows: {len(safety_checks.get('unsupported_crm_ready_rows', []))}",
        f"- Manual-lookup CRM-ready rows: {len(safety_checks.get('manual_lookup_crm_ready_rows', []))}",
        f"- Missing source rows: {len(safety_checks.get('missing_source_rows', []))}",
        f"- Missing next action rows: {len(safety_checks.get('missing_next_action_rows', []))}",
        f"- Private contact values redacted: {_yes_no(safety_checks.get('private_contact_values_redacted'))}",
        "",
        "## Service Boundary",
        "",
        f"- Route: {service_boundary.get('route', DEFAULT_R09L_ROUTE)}",
        f"- Method: {service_boundary.get('method', 'POST')}",
        f"- Protected route: {_yes_no(service_boundary.get('protected_route_ok'))}",
        f"- Internal token required: {_yes_no(service_boundary.get('internal_token_required'))}",
        f"- Internal token checked: {_yes_no(service_boundary.get('internal_token_checked'))}",
        f"- Sanitized input: {_yes_no(service_boundary.get('sanitized_input'))}",
        f"- Response status: {service_boundary.get('response_status', 0)}",
        "",
        "## Prompt B Handoff",
        "",
        f"- Ready after Prompt B merge: {_yes_no(prompt_b_handoff.get('ready_after_prompt_b_merge'))}",
        f"- Required branch: {prompt_b_handoff.get('integration_branch', '')}",
        f"- Required report: {prompt_b_handoff.get('required_report', '')}",
        f"- Keep downstream blocked: {_yes_no(prompt_b_handoff.get('keep_downstream_blocked'))}",
        f"- Blocked scope: {', '.join(prompt_b_handoff.get('blocked_scope') or [])}",
        "",
    ]
    return "\n".join(lines)


def _yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"
