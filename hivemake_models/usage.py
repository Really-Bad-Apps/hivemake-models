"""Storage-usage measurement records (STORAGE-METERING.md).

A `UsageRun` is one sweep of the knowledge layer; each sweep writes one
`HiveUsageSnapshot` per hive. `OwnerUsage` is the rollup the API returns.

Two distinctions in here are easy to flatten by accident, and both change what
a number means:

- **Rows are not graph objects.** cognee's `nodes`/`edges` tables are an
  ownership ledger: one entity mentioned in 100 documents is 100 rows but one
  graph node. Rows are what occupy disk, so metering counts rows — hence
  `node_row_count`, not `node_count`.
- **Measured is not apportioned.** Most bytes belong to exactly one hive.
  A small remainder is shared between hives and split; the rest belongs to
  nobody and is platform overhead. They are separate fields so a bill can show
  what is certain apart from what was divided up.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from hivemake_models.enums import UsageRunStatus


@dataclass
class UsageRun:
    """One measurement sweep.

    `coverage` fields are the run's own audit: `attributed_bytes +
    overhead_bytes` should account for `cognee_db_total_bytes`, and
    `edge_vector_match_ratio` is the share of edge vectors the text join
    resolved to a hive. A run whose join quietly stops working does not error —
    it moves bytes from attributed to overhead and under-bills everyone — so
    the ratio is recorded on every run and checked against a floor.
    """
    id: UUID
    started_at: int
    status: UsageRunStatus
    method_version: str
    finished_at: Optional[int] = None
    cognee_db_total_bytes: Optional[int] = None
    attributed_bytes: Optional[int] = None
    overhead_bytes: Optional[int] = None
    bytes_per_edge_vector: Optional[int] = None
    # Stored as DOUBLE PRECISION, not NUMERIC: psycopg2 hands NUMERIC back as
    # `Decimal`, which would make this field a Decimal at runtime despite the
    # annotation — the same trap as an enum-typed field holding a plain str.
    # A ratio needs no exact-decimal semantics.
    edge_vector_match_ratio: Optional[float] = None
    error: Optional[str] = None


@dataclass
class HiveUsageSnapshot:
    """One hive's footprint as of one run.

    `hive_slug` and `owner_user_id` are copied at measurement time rather than
    joined at read time: a usage history has to stay readable after a hive is
    renamed, or deleted outright.
    """
    id: UUID
    run_id: UUID
    hive_id: UUID
    hive_slug: str
    measured_at: int
    node_row_count: int
    edge_row_count: int
    # Field order deliberately mirrors the column order in migration 028.
    # Construction is by keyword everywhere, so this is not load-bearing today
    # — but `exact_bytes` and `edge_vector_bytes` differ by roughly 60x, so a
    # future positional build would be quietly wrong rather than loudly broken.
    exact_bytes: int
    edge_vector_bytes: int
    shared_entity_bytes: int
    shared_edge_vector_bytes: int
    total_bytes: int
    owner_user_id: Optional[UUID] = None
    # NULL while Neo4j is reported as platform overhead rather than billed.
    estimated_graph_bytes: Optional[int] = None


@dataclass
class OwnerUsage:
    """What one owner is using, across every hive they own.

    An owner pays once for an object however many of their own hives reference
    it; an object shared between two owners counts half to each. That rule is
    applied while measuring, so these totals are a plain sum of the snapshots
    and never double-count.
    """
    owner_user_id: UUID
    measured_at: int
    total_bytes: int
    exact_bytes: int
    apportioned_bytes: int
    hives: list[HiveUsageSnapshot]
    # False while Neo4j is excluded, so a caller can tell "this is the whole
    # footprint" from "this is the Postgres share of it".
    includes_graph_store: bool = False
