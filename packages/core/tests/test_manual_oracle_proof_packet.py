from __future__ import annotations

import json

from core.manual_oracle_proof_packet import (
    build_manual_oracle_proof_packet,
    write_r09h_proof_packet_artifacts,
)


def test_r09h_proof_packet_replays_manual_oracle_workbook_structure():
    packet = build_manual_oracle_proof_packet()
    payload = packet.to_payload()

    assert packet.passes() is True
    assert payload["feature_id"] == "R09H - Manual-oracle proof replay gate packet"
    assert payload["manual_oracle_replay"]["structure_reproduced"] is True
    assert payload["manual_oracle_replay"]["observed_rows"] == 17
    assert payload["manual_oracle_replay"]["verified_contact_rows"] == 10
    assert payload["manual_oracle_replay"]["manual_lookup_rows"] == 7
    assert payload["source_assisted_replay"]["candidate_count"] == 17
    assert payload["source_assisted_replay"]["tier_distribution"]["high_trust_usable"] == 10
    assert payload["source_assisted_replay"]["tier_distribution"]["manual_lookup"] == 7
    assert payload["source_assisted_replay"]["blocked_source_urls"] == []
    assert payload["workbook_replay"]["row_count"] == 17
    assert payload["workbook_replay"]["tier_distribution"]["READY_WITH_CONTACT"] == 10
    assert payload["workbook_replay"]["tier_distribution"]["MANUAL_LOOKUP"] == 7
    assert payload["workbook_replay"]["downgraded_ready_rows"] == []
    assert payload["safety_checks"]["unsupported_crm_ready_rows"] == []
    assert payload["safety_checks"]["manual_lookup_crm_ready_rows"] == []
    assert payload["safety_checks"]["missing_source_rows"] == []
    assert payload["safety_checks"]["missing_next_action_rows"] == []
    assert payload["safety_checks"]["private_contact_values_redacted"] is True
    assert payload["prompt_c_handoff"]["ready_after_prompt_b_merge"] is True
    assert payload["prompt_c_handoff"]["keep_downstream_blocked"] is True


def test_r09h_proof_packet_keeps_latest_zero_contact_live_evidence_as_hold_signal():
    packet = build_manual_oracle_proof_packet(
        live_quality_summary={
            "artifact_path": "audits/raw/reset-2026-05-10/r09a/live-prompt-b/quality-summary.json",
            "case_summaries": {
                "finance-cisos-new-york": {
                    "high_trust_usable_count": 0,
                    "funnel_counts": {"contact_quality_passes": 0},
                    "quality_report": {"contact_quality_count": 0},
                }
            },
        },
        live_service_status={
            "credentials_present": True,
            "api_health_checked": True,
            "api_health_status": "000",
            "fresh_live_benchmark_run": False,
        },
    )
    payload = packet.to_payload()

    assert payload["passes"] is True
    assert payload["live_source_assisted_status"]["credentials_present"] is True
    assert payload["live_source_assisted_status"]["api_health_status"] == "000"
    assert payload["live_source_assisted_status"]["fresh_live_benchmark_run"] is False
    assert payload["live_source_assisted_status"]["latest_saved_live_high_trust_usable_rows"] == 0
    assert payload["live_source_assisted_status"]["latest_saved_live_contact_quality_passes"] == 0
    assert payload["rg3_recommendation"].startswith("hold_pending_prompt_c_live_audit")


def test_r09h_proof_packet_writes_json_and_markdown_artifacts(tmp_path):
    packet = build_manual_oracle_proof_packet(generated_at="2026-05-11T12:00:00Z")

    paths = write_r09h_proof_packet_artifacts(tmp_path, packet=packet)
    json_payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    markdown_text = paths["markdown"].read_text(encoding="utf-8")

    assert json_payload["packet_id"] == "r09h_manual_oracle_proof_replay_gate_packet"
    assert json_payload["passes"] is True
    assert "R09H Manual-Oracle Proof Replay Gate Packet" in markdown_text
    assert "READY_WITH_CONTACT: 10" in markdown_text
    assert "MANUAL_LOOKUP: 7" in markdown_text
    assert "Unsupported CRM-ready contacts: 0" in markdown_text
    assert "Keep downstream blocked: yes" in markdown_text
