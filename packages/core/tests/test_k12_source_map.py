from __future__ import annotations

from core.k12_source_map import (
    GENERIC_SEARCH_FAMILIES,
    collect_k12_roster_sources,
    load_az_k12_source_map,
    load_nm_k12_source_map,
    replay_k12_source_map,
)
from core.query_planner import ARIZONA_K12_TARGET_ACCOUNTS


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


def test_az_k12_source_map_covers_all_benchmark_districts_with_official_families():
    source_map = load_az_k12_source_map()

    assert source_map.map_id == "az_k12_source_map_rg6r3"
    assert source_map.state == "AZ"

    districts_by_name = {district.name: district for district in source_map.districts}
    assert set(ARIZONA_K12_TARGET_ACCOUNTS) <= set(districts_by_name)

    for account in ARIZONA_K12_TARGET_ACCOUNTS:
        district = districts_by_name[account]
        assert district.expected_source_families
        assert {"district_staff_directory", "district_technology_page"} & set(
            district.expected_source_families
        )
        assert district.sources
        assert district.sources[0].source_family in {
            "district_staff_directory",
            "district_technology_page",
            "district_leadership_page",
            "district_board_agenda_pdf",
        }
        assert all(source.source_family not in GENERIC_SEARCH_FAMILIES for source in district.sources)
        assert all(
            source.source_reputation_signal
            in {"official_state_agency", "official_district", "official_public_document"}
            for source in district.sources
        )


def test_az_k12_source_map_replay_is_roster_first_without_generic_fallbacks():
    source_map = load_az_k12_source_map()
    seeds = collect_k12_roster_sources(source_map)
    summary = replay_k12_source_map(source_map)

    assert summary.passes() is True
    assert summary.district_count == len(ARIZONA_K12_TARGET_ACCOUNTS) + 1
    assert summary.official_seed_count == summary.seed_count == len(seeds)
    assert summary.state_roster_seed_count == 1
    assert summary.generic_search_sources == ()
    assert summary.districts_missing_roster_first_sources == ()
    assert "district_technology_page" in summary.source_families
    assert "district_staff_directory" in summary.source_families
