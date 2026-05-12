from __future__ import annotations

import json

from core.live_source_assisted_proof import (
    DEFAULT_R09L_QUERY,
    DEFAULT_R09L_TARGET,
    build_live_source_assisted_proof,
    write_r09l_proof_artifacts,
)


def test_r09l_live_source_assisted_proof_replays_source_map_and_workbook_shape():
    packet = build_live_source_assisted_proof()
    payload = packet.to_payload()

    assert packet.passes() is True
    assert payload["feature_id"] == "R09L - Live source-assisted product proof"
    assert payload["request_summary"]["query"] == DEFAULT_R09L_QUERY
    assert payload["request_summary"]["target"] == DEFAULT_R09L_TARGET
    assert payload["source_map_replay"]["source_map_reproduced"] is True
    assert payload["source_map_replay"]["generic_search_sources"] == []
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
    assert payload["service_boundary"]["protected_route_ok"] is True
    assert payload["service_boundary"]["internal_token_required"] is True
    assert payload["service_boundary"]["internal_token_checked"] is True
    assert payload["service_boundary"]["response_status"] == 200
    assert payload["prompt_b_handoff"]["ready_after_prompt_b_merge"] is True
    assert payload["prompt_b_handoff"]["keep_downstream_blocked"] is True

    ready_row = next(row for row in payload["workbook_replay"]["rows"] if row["workbook_tier"] == "READY_WITH_CONTACT")
    manual_row = next(row for row in payload["workbook_replay"]["rows"] if row["workbook_tier"] == "MANUAL_LOOKUP")
    assert ready_row["crm_ready"] is True
    assert ready_row["source_name_url"]
    assert ready_row["source_title_url"]
    assert ready_row["source_org_url"]
    assert ready_row["source_email_url"]
    assert manual_row["crm_ready"] is False
    assert manual_row["source_org_url"]
    assert manual_row["blocker_notes"]
    assert manual_row["next_action"]
    assert "CRM import blocked" in manual_row["validation_notes"]


def test_r09l_proof_packet_writes_json_and_markdown_artifacts(tmp_path):
    packet = build_live_source_assisted_proof(generated_at="2026-05-11T12:00:00Z")

    paths = write_r09l_proof_artifacts(tmp_path, packet=packet)
    json_payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    markdown_text = paths["markdown"].read_text(encoding="utf-8")

    assert json_payload["packet_id"] == "r09l_live_source_assisted_product_proof"
    assert json_payload["passes"] is True
    assert "R09L Live Source-Assisted Product Proof" in markdown_text
    assert "READY_WITH_CONTACT: 10" in markdown_text
    assert "MANUAL_LOOKUP: 7" in markdown_text
    assert "Protected route: yes" in markdown_text
    assert "Private contact values redacted: yes" in markdown_text
    assert "Keep downstream blocked: yes" in markdown_text
