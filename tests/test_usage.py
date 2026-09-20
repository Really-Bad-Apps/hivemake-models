from uuid import uuid4

from hivemake_models import (
    HiveUsageSnapshot,
    OwnerUsage,
    UsageRun,
    UsageRunStatus,
)


def _snapshot(
    run_id=None,
    hive_id=None,
    owner_user_id=None,
    exact_bytes: int = 100,
    shared_entity_bytes: int = 10,
    edge_vector_bytes: int = 500,
    shared_edge_vector_bytes: int = 5,
) -> HiveUsageSnapshot:
    total = (
        exact_bytes
        + shared_entity_bytes
        + edge_vector_bytes
        + shared_edge_vector_bytes
    )
    return HiveUsageSnapshot(
        id=uuid4(),
        run_id=run_id or uuid4(),
        hive_id=hive_id or uuid4(),
        hive_slug="really-bad-apps",
        measured_at=1789916343,
        node_row_count=81952,
        edge_row_count=320917,
        exact_bytes=exact_bytes,
        shared_entity_bytes=shared_entity_bytes,
        edge_vector_bytes=edge_vector_bytes,
        shared_edge_vector_bytes=shared_edge_vector_bytes,
        total_bytes=total,
        owner_user_id=owner_user_id,
    )


class TestUsageRun:
    def test_a_running_sweep_carries_no_measurements_yet(self) -> None:
        run = UsageRun(
            id=uuid4(),
            started_at=1789916343,
            status=UsageRunStatus.RUNNING,
            method_version="2026-09-20",
        )
        assert run.finished_at is None
        assert run.attributed_bytes is None
        assert run.edge_vector_match_ratio is None
        assert run.error is None

    def test_carries_its_own_coverage_audit(self) -> None:
        """The match ratio is the guard that matters: a broken text join does
        not raise, it just moves bytes into overhead."""
        run = UsageRun(
            id=uuid4(),
            started_at=1789916343,
            status=UsageRunStatus.SUCCEEDED,
            method_version="2026-09-20",
            finished_at=1789916400,
            cognee_db_total_bytes=3_760_291_840,
            attributed_bytes=3_300_000_000,
            overhead_bytes=460_291_840,
            bytes_per_edge_vector=6148,
            edge_vector_match_ratio=0.8797,
        )
        assert run.attributed_bytes + run.overhead_bytes == run.cognee_db_total_bytes
        assert run.edge_vector_match_ratio < 1.0

    def test_failed_run_keeps_the_reason(self) -> None:
        run = UsageRun(
            id=uuid4(),
            started_at=1789916343,
            status=UsageRunStatus.FAILED,
            method_version="2026-09-20",
            finished_at=1789916350,
            error="edge_vector_match_ratio 0.31 below floor 0.70",
        )
        assert run.status is UsageRunStatus.FAILED
        assert "below floor" in run.error


class TestHiveUsageSnapshot:
    def test_counts_are_ledger_rows_not_graph_objects(self) -> None:
        """Rows occupy disk whether or not they duplicate a graph node, so
        metering counts rows. The field names say so."""
        snapshot = _snapshot()
        assert snapshot.node_row_count == 81952
        assert not hasattr(snapshot, "node_count")

    def test_apportioned_bytes_are_separable_from_measured_ones(self) -> None:
        snapshot = _snapshot(
            exact_bytes=1000,
            shared_entity_bytes=7,
            edge_vector_bytes=2000,
            shared_edge_vector_bytes=3,
        )
        apportioned = snapshot.shared_entity_bytes + snapshot.shared_edge_vector_bytes
        assert apportioned == 10
        assert snapshot.total_bytes == 3010

    def test_graph_bytes_default_to_none_while_neo4j_is_overhead(self) -> None:
        assert _snapshot().estimated_graph_bytes is None

    def test_owner_may_be_absent(self) -> None:
        """A hive whose sole owner was deleted upstream still gets measured —
        its usage becomes unattributed rather than vanishing."""
        assert _snapshot(owner_user_id=None).owner_user_id is None


class TestOwnerUsage:
    def test_totals_are_a_plain_sum_of_snapshots(self) -> None:
        owner = uuid4()
        run = uuid4()
        first = _snapshot(run_id=run, owner_user_id=owner, exact_bytes=100)
        second = _snapshot(run_id=run, owner_user_id=owner, exact_bytes=250)
        usage = OwnerUsage(
            owner_user_id=owner,
            measured_at=1789916343,
            total_bytes=first.total_bytes + second.total_bytes,
            exact_bytes=first.exact_bytes + second.exact_bytes,
            apportioned_bytes=30,
            hives=[first, second],
        )
        assert usage.total_bytes == sum(h.total_bytes for h in usage.hives)
        assert usage.exact_bytes == 350

    def test_says_whether_the_graph_store_is_included(self) -> None:
        """So a reader can tell a whole footprint from the Postgres share."""
        usage = OwnerUsage(
            owner_user_id=uuid4(),
            measured_at=1789916343,
            total_bytes=0,
            exact_bytes=0,
            apportioned_bytes=0,
            hives=[],
        )
        assert usage.includes_graph_store is False
