from __future__ import annotations

from core.k12_source_map import (
    GENERIC_SEARCH_FAMILIES,
    collect_k12_roster_sources,
    load_nm_k12_source_map,
    replay_k12_source_map,
)


def test_nm_k12_source_map_is_roster_first_and_auditable():
    source_map = load_nm_k12_source_map()

    assert source_map.map_id == "nm_k12_source_map_r09e"
    assert source_map.state == "NM"
    assert len(source_map.districts) >= 7

    for district in source_map.districts:
        assert district.expected_source_families
        assert district.sources
        for source in district.sources:
            assert source.source_family not in GENERIC_SEARCH_FAMILIES
            assert source.access_status
            assert source.source_reputation_signal in {
                "official_state_agency",
                "official_district",
                "official_public_document",
            }
            assert source.crawl_method
            assert source.extraction_method
            assert source.supports


def test_collect_k12_roster_sources_prioritizes_official_roster_sources():
    source_map = load_nm_k12_source_map()
    seeds = collect_k12_roster_sources(source_map)

    assert seeds
    assert seeds[0].district_name == "New Mexico Public Education Department"
    assert seeds[0].source_family == "state_education_agency_roster"
    assert seeds[0].url.startswith("https://web.ped.nm.gov/")
    assert all(seed.source_family not in GENERIC_SEARCH_FAMILIES for seed in seeds)
    assert all(seed.source_reputation_signal.startswith("official_") for seed in seeds)
    assert len({seed.seed_id for seed in seeds}) == len(seeds)


def test_replay_k12_source_map_reports_coverage_and_gaps():
    summary = replay_k12_source_map()

    assert summary.passes() is True
    assert summary.district_count >= 7
    assert summary.seed_count >= 13
    assert summary.official_seed_count == summary.seed_count
    assert summary.state_roster_seed_count == 1
    assert summary.districts_missing_roster_first_sources == ()
    assert summary.generic_search_sources == ()
    assert "state_education_agency_roster" in summary.source_families
    assert "district_staff_directory" in summary.source_families
    assert any("manual_lookup" in gap for gap in summary.coverage_gaps)
