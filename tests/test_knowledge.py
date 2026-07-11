from uuid import uuid4

from hivemake_models import KnowledgeMatch


class TestKnowledgeMatch:
    def test_create_full(self) -> None:
        match = KnowledgeMatch(
            ticket_id=uuid4(),
            hive_id=uuid4(),
            ticket_type="bug",
            final_status="resolved",
            score=0.87,
            snippet="DB connections exhausted under burst load...",
            project="auth-svc",
        )
        assert match.ticket_type == "bug"
        assert match.project == "auth-svc"
        assert match.score == 0.87

    def test_project_defaults_to_none(self) -> None:
        # Hive-level tickets (no project association) are legitimate;
        # the recall path must be able to surface them without a project.
        match = KnowledgeMatch(
            ticket_id=uuid4(),
            hive_id=uuid4(),
            ticket_type="feature",
            final_status="closed",
            score=0.42,
            snippet="Hive-level operational request",
        )
        assert match.project is None
