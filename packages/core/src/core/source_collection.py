from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from .query_planner import QueryPlan

SOURCE_COLLECTION_SCHEMA_VERSION = "source_collection.v1"


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _source_id(url: str, title: str) -> str:
    identity = f"{url.strip().lower()}|{title.strip().lower()}"
    return f"src_{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"


def query_plan_to_payload(query_plan: QueryPlan | None) -> dict[str, Any] | None:
    if query_plan is None:
        return None
    return asdict(query_plan)


class CollectedSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(description="Stable ID derived from the source URL and title.")
    rank: int = Field(ge=1, description="One-based rank in the deduped collected source list.")
    title: str = Field(default="", description="Search-result title.")
    url: str = Field(default="", description="Search-result URL.")
    content: str = Field(default="", description="Search-result content returned by the vendor.")
    score: float = Field(default=0.0, description="Vendor relevance score when available.")
    vendor_query: str = Field(default="", description="Vendor query that first surfaced the source.")
    matched_vendor_queries: list[str] = Field(
        default_factory=list,
        description="All vendor queries that matched this source before dedupe.",
    )
    content_sha256: str = Field(description="Hash of the stored content for replay integrity.")


class SourceCollectionSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = SOURCE_COLLECTION_SCHEMA_VERSION
    query: str = Field(description="Original operator query.")
    collected_at: str = Field(description="UTC timestamp when the source snapshot was built.")
    requested_max_results: int = Field(ge=1, description="Requested raw search-result ceiling.")
    returned_source_count: int = Field(ge=0, description="Number of deduped sources in this snapshot.")
    tavily_searches: int = Field(ge=0, description="Number of vendor searches executed.")
    search_depth: str = Field(description="Vendor search-depth setting.")
    query_plan: dict[str, Any] | None = Field(default=None, description="Compiled query plan payload.")
    sources: list[CollectedSource] = Field(default_factory=list, description="Deduped collected sources.")


class SourceSnapshotStore(Protocol):
    def save(self, snapshot: SourceCollectionSnapshot) -> None:
        """Persist a source snapshot for replay/audit."""


class InMemorySourceSnapshotStore:
    def __init__(self) -> None:
        self.snapshots: list[SourceCollectionSnapshot] = []

    def save(self, snapshot: SourceCollectionSnapshot) -> None:
        self.snapshots.append(snapshot)


class JsonlSourceSnapshotStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, snapshot: SourceCollectionSnapshot) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot.model_dump(), sort_keys=True))
            handle.write("\n")


def build_source_collection_snapshot(
    *,
    query: str,
    results: list[dict[str, Any]],
    requested_max_results: int,
    tavily_searches: int,
    search_depth: str,
    query_plan: QueryPlan | None,
    collected_at: str | None = None,
) -> SourceCollectionSnapshot:
    sources = [
        CollectedSource(
            source_id=_source_id(str(result.get("url", "")), str(result.get("title", ""))),
            rank=index,
            title=str(result.get("title", "")),
            url=str(result.get("url", "")),
            content=str(result.get("content", "")),
            score=float(result.get("score", 0.0) or 0.0),
            vendor_query=str(result.get("vendor_query", "")),
            matched_vendor_queries=[str(query) for query in result.get("matched_vendor_queries", [])],
            content_sha256=_content_hash(str(result.get("content", ""))),
        )
        for index, result in enumerate(results, start=1)
    ]

    return SourceCollectionSnapshot(
        query=query,
        collected_at=collected_at or _utc_now(),
        requested_max_results=requested_max_results,
        returned_source_count=len(sources),
        tavily_searches=tavily_searches,
        search_depth=search_depth,
        query_plan=query_plan_to_payload(query_plan),
        sources=sources,
    )
