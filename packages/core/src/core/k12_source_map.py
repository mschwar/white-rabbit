from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_K12_SOURCE_MAP_PATH = _REPO_ROOT / "packages/core/tests/fixtures/nm_k12_source_map.json"
DEFAULT_AZ_K12_SOURCE_MAP_PATH = _REPO_ROOT / "packages/core/tests/fixtures/az_k12_source_map.json"

ROSTER_FIRST_FAMILIES = {
    "state_education_agency_roster",
    "state_public_school_directory",
    "district_official_homepage",
    "district_staff_directory",
    "district_technology_page",
    "district_leadership_page",
    "district_board_agenda_pdf",
    "district_contact_page",
    "manual_oracle_seed",
}

GENERIC_SEARCH_FAMILIES = {"generic_tavily_search", "generic_web_search", "llm_browse"}
OFFICIAL_REPUTATION_SIGNALS = {"official_state_agency", "official_district", "official_public_document"}


@dataclass(frozen=True, slots=True)
class K12SourceFamily:
    family_id: str
    source_family: str
    priority: int
    url: str
    access_status: str
    source_reputation_signal: str
    crawl_method: str
    extraction_method: str
    supports: tuple[str, ...]
    notes: str = ""

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> K12SourceFamily:
        return cls(
            family_id=str(payload["family_id"]),
            source_family=str(payload["source_family"]),
            priority=int(payload["priority"]),
            url=str(payload["url"]),
            access_status=str(payload["access_status"]),
            source_reputation_signal=str(payload["source_reputation_signal"]),
            crawl_method=str(payload["crawl_method"]),
            extraction_method=str(payload["extraction_method"]),
            supports=tuple(str(item) for item in payload.get("supports", [])),
            notes=str(payload.get("notes", "")),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "source_family": self.source_family,
            "priority": self.priority,
            "url": self.url,
            "access_status": self.access_status,
            "source_reputation_signal": self.source_reputation_signal,
            "crawl_method": self.crawl_method,
            "extraction_method": self.extraction_method,
            "supports": list(self.supports),
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class K12DistrictTarget:
    district_id: str
    name: str
    state: str
    manual_oracle_row_ids: tuple[str, ...]
    expected_source_families: tuple[str, ...]
    sources: tuple[K12SourceFamily, ...]
    coverage_gaps: tuple[str, ...] = ()

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> K12DistrictTarget:
        return cls(
            district_id=str(payload["district_id"]),
            name=str(payload["name"]),
            state=str(payload["state"]),
            manual_oracle_row_ids=tuple(str(item) for item in payload.get("manual_oracle_row_ids", [])),
            expected_source_families=tuple(str(item) for item in payload.get("expected_source_families", [])),
            sources=tuple(K12SourceFamily.from_payload(item) for item in payload.get("sources", [])),
            coverage_gaps=tuple(str(item) for item in payload.get("coverage_gaps", [])),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "district_id": self.district_id,
            "name": self.name,
            "state": self.state,
            "manual_oracle_row_ids": list(self.manual_oracle_row_ids),
            "expected_source_families": list(self.expected_source_families),
            "sources": [source.to_payload() for source in self.sources],
            "coverage_gaps": list(self.coverage_gaps),
        }


@dataclass(frozen=True, slots=True)
class K12SourceMap:
    map_id: str
    state: str
    vertical: str
    source_authority_note: str
    districts: tuple[K12DistrictTarget, ...]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> K12SourceMap:
        return cls(
            map_id=str(payload["map_id"]),
            state=str(payload["state"]),
            vertical=str(payload["vertical"]),
            source_authority_note=str(payload["source_authority_note"]),
            districts=tuple(K12DistrictTarget.from_payload(item) for item in payload.get("districts", [])),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "map_id": self.map_id,
            "state": self.state,
            "vertical": self.vertical,
            "source_authority_note": self.source_authority_note,
            "districts": [district.to_payload() for district in self.districts],
        }


@dataclass(frozen=True, slots=True)
class K12RosterSeed:
    seed_id: str
    district_id: str
    district_name: str
    source_family: str
    url: str
    access_status: str
    source_reputation_signal: str
    crawl_method: str
    extraction_method: str
    priority: int
    supports: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "seed_id": self.seed_id,
            "district_id": self.district_id,
            "district_name": self.district_name,
            "source_family": self.source_family,
            "url": self.url,
            "access_status": self.access_status,
            "source_reputation_signal": self.source_reputation_signal,
            "crawl_method": self.crawl_method,
            "extraction_method": self.extraction_method,
            "priority": self.priority,
            "supports": list(self.supports),
        }


@dataclass(frozen=True, slots=True)
class K12SourceMapReplaySummary:
    map_id: str
    district_count: int
    seed_count: int
    official_seed_count: int
    state_roster_seed_count: int
    districts_with_roster_first_sources: tuple[str, ...]
    districts_missing_roster_first_sources: tuple[str, ...]
    source_families: tuple[str, ...]
    generic_search_sources: tuple[str, ...]
    coverage_gaps: tuple[str, ...]
    source_map_reproduced: bool

    def passes(self) -> bool:
        return self.source_map_reproduced

    def to_payload(self) -> dict[str, Any]:
        return {
            "map_id": self.map_id,
            "district_count": self.district_count,
            "seed_count": self.seed_count,
            "official_seed_count": self.official_seed_count,
            "state_roster_seed_count": self.state_roster_seed_count,
            "districts_with_roster_first_sources": list(self.districts_with_roster_first_sources),
            "districts_missing_roster_first_sources": list(self.districts_missing_roster_first_sources),
            "source_families": list(self.source_families),
            "generic_search_sources": list(self.generic_search_sources),
            "coverage_gaps": list(self.coverage_gaps),
            "source_map_reproduced": self.source_map_reproduced,
        }


def load_nm_k12_source_map(path: Path | None = None) -> K12SourceMap:
    fixture_path = path or DEFAULT_K12_SOURCE_MAP_PATH
    return K12SourceMap.from_payload(json.loads(fixture_path.read_text(encoding="utf-8")))


def load_az_k12_source_map(path: Path | None = None) -> K12SourceMap:
    fixture_path = path or DEFAULT_AZ_K12_SOURCE_MAP_PATH
    return K12SourceMap.from_payload(json.loads(fixture_path.read_text(encoding="utf-8")))


def collect_k12_roster_sources(source_map: K12SourceMap) -> list[K12RosterSeed]:
    seeds: list[K12RosterSeed] = []
    seen: set[tuple[str, str]] = set()

    for district in source_map.districts:
        for source in sorted(district.sources, key=lambda item: item.priority):
            if source.source_family in GENERIC_SEARCH_FAMILIES:
                continue
            if source.source_family not in ROSTER_FIRST_FAMILIES:
                continue
            identity = (district.district_id, _normalize_url(source.url))
            if identity in seen:
                continue
            seen.add(identity)
            seeds.append(
                K12RosterSeed(
                    seed_id=_seed_id(district.district_id, source.url),
                    district_id=district.district_id,
                    district_name=district.name,
                    source_family=source.source_family,
                    url=source.url,
                    access_status=source.access_status,
                    source_reputation_signal=source.source_reputation_signal,
                    crawl_method=source.crawl_method,
                    extraction_method=source.extraction_method,
                    priority=source.priority,
                    supports=source.supports,
                )
            )

    return seeds


def replay_k12_source_map(source_map: K12SourceMap | None = None) -> K12SourceMapReplaySummary:
    source_map = source_map or load_nm_k12_source_map()
    seeds = collect_k12_roster_sources(source_map)
    seed_lookup = _seeds_by_district(seeds)
    districts_with_roster_first_sources: list[str] = []
    districts_missing_roster_first_sources: list[str] = []
    coverage_gaps: list[str] = []

    for district in source_map.districts:
        district_seeds = seed_lookup.get(district.district_id, [])
        families = {seed.source_family for seed in district_seeds}
        if _has_required_roster_first_family(families, district.expected_source_families):
            districts_with_roster_first_sources.append(district.name)
        else:
            districts_missing_roster_first_sources.append(district.name)

        for gap in district.coverage_gaps:
            coverage_gaps.append(f"{district.name}: {gap}")

    source_families = sorted({seed.source_family for seed in seeds})
    generic_search_sources = [
        f"{district.name}: {source.url}"
        for district in source_map.districts
        for source in district.sources
        if source.source_family in GENERIC_SEARCH_FAMILIES
    ]
    official_seed_count = sum(
        1 for seed in seeds if seed.source_reputation_signal in OFFICIAL_REPUTATION_SIGNALS
    )
    state_roster_seed_count = sum(
        1 for seed in seeds if seed.source_family == "state_education_agency_roster"
    )

    source_map_reproduced = (
        len(districts_with_roster_first_sources) == len(source_map.districts)
        and not districts_missing_roster_first_sources
        and not generic_search_sources
        and official_seed_count == len(seeds)
        and state_roster_seed_count >= 1
    )

    return K12SourceMapReplaySummary(
        map_id=source_map.map_id,
        district_count=len(source_map.districts),
        seed_count=len(seeds),
        official_seed_count=official_seed_count,
        state_roster_seed_count=state_roster_seed_count,
        districts_with_roster_first_sources=tuple(districts_with_roster_first_sources),
        districts_missing_roster_first_sources=tuple(districts_missing_roster_first_sources),
        source_families=tuple(source_families),
        generic_search_sources=tuple(generic_search_sources),
        coverage_gaps=tuple(coverage_gaps),
        source_map_reproduced=source_map_reproduced,
    )


def _seeds_by_district(seeds: Iterable[K12RosterSeed]) -> dict[str, list[K12RosterSeed]]:
    seeds_by_district: dict[str, list[K12RosterSeed]] = {}
    for seed in seeds:
        seeds_by_district.setdefault(seed.district_id, []).append(seed)
    return seeds_by_district


def _has_required_roster_first_family(
    actual_families: set[str],
    expected_families: Iterable[str],
) -> bool:
    expected = set(expected_families)
    return bool(expected) and expected.issubset(actual_families)


def _seed_id(district_id: str, url: str) -> str:
    identity = f"{district_id.strip().lower()}|{_normalize_url(url)}"
    return f"k12src_{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"


def _normalize_url(url: str) -> str:
    return url.strip().lower().rstrip("/")
