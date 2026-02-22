from uuid import uuid4

from hivemake_models.enums import (
    AgentStatus,
    LearningCategory,
    NegotiationAction,
    ProjectStatus,
    TicketPriority,
    TicketStatus,
    TicketType,
    TenantStatus,
    UserRole,
    UserStatus,
)
from hivemake_models.models import (
    Agent,
    AgentLearning,
    Negotiation,
    Project,
    ProjectDependency,
    Tenant,
    Ticket,
    TicketHistory,
    User,
)


class TestTenant:
    def test_create(self) -> None:
        tenant = Tenant(
            id=uuid4(),
            aegis_site_id=1,
            name="Acme Corp",
            slug="acme-corp",
            status=TenantStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert tenant.name == "Acme Corp"
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.status == "active"


class TestUser:
    def test_create(self) -> None:
        tenant_id = uuid4()
        user = User(
            id=uuid4(),
            tenant_id=tenant_id,
            aegis_user_id=42,
            email="jason@acme.com",
            display_name="Jason",
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert user.role == UserRole.OWNER
        assert user.tenant_id == tenant_id


class TestProject:
    def test_create_with_description(self) -> None:
        project = Project(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Web App",
            slug="web-app",
            status=ProjectStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            description="The main web application",
        )
        assert project.description == "The main web application"

    def test_create_without_description(self) -> None:
        project = Project(
            id=uuid4(),
            tenant_id=uuid4(),
            name="Web App",
            slug="web-app",
            status=ProjectStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert project.description is None


class TestAgent:
    def test_create_with_defaults(self) -> None:
        agent = Agent(
            id=uuid4(),
            tenant_id=uuid4(),
            project_id=uuid4(),
            name="App Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert agent.config == {}
        assert agent.gatekeeper_client_id is None
        assert agent.description is None

    def test_create_with_config(self) -> None:
        config = {
            "gated_actions": [
                {
                    "action": "merge_pr",
                    "approval_target": {"agent_id": str(uuid4())},
                }
            ],
            "redirect_rules": {"max_redirects": 3},
        }
        agent = Agent(
            id=uuid4(),
            tenant_id=uuid4(),
            project_id=uuid4(),
            name="App Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            config=config,
        )
        assert len(agent.config["gated_actions"]) == 1
        assert agent.config["redirect_rules"]["max_redirects"] == 3


class TestProjectDependency:
    def test_create(self) -> None:
        dep = ProjectDependency(
            id=uuid4(),
            tenant_id=uuid4(),
            project_id=uuid4(),
            depends_on_project_id=uuid4(),
            created_at=1700000000,
        )
        assert dep.project_id != dep.depends_on_project_id


class TestAgentLearning:
    def test_create_with_category(self) -> None:
        learning = AgentLearning(
            id=uuid4(),
            tenant_id=uuid4(),
            agent_id=uuid4(),
            content="When ORM errors appear, redirect to the data-layer agent",
            active=True,
            created_at=1700000000,
            updated_at=1700000000,
            category=LearningCategory.ROUTING,
            source_ticket_id=uuid4(),
        )
        assert learning.category == LearningCategory.ROUTING
        assert learning.active is True

    def test_create_without_optional_fields(self) -> None:
        learning = AgentLearning(
            id=uuid4(),
            tenant_id=uuid4(),
            agent_id=uuid4(),
            content="Memory leak pattern detected in connection pool",
            active=True,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert learning.category is None
        assert learning.source_ticket_id is None


class TestTicket:
    def test_create_minimal(self) -> None:
        ticket = Ticket(
            id=uuid4(),
            tenant_id=uuid4(),
            project_id=uuid4(),
            created_by_agent_id=uuid4(),
            ticket_type=TicketType.BUG,
            title="NullPointerException in user service",
            description="Stack trace shows NPE on line 42",
            priority=TicketPriority.HIGH,
            status=TicketStatus.OPEN,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert ticket.assigned_agent_id is None
        assert ticket.pending_approval_from_agent_id is None
        assert ticket.pending_approval_from_user_id is None
        assert ticket.resolution is None

    def test_create_with_approval_fields(self) -> None:
        approver_id = uuid4()
        ticket = Ticket(
            id=uuid4(),
            tenant_id=uuid4(),
            project_id=uuid4(),
            created_by_agent_id=uuid4(),
            ticket_type=TicketType.TASK,
            title="Deploy v2.1",
            description="Deploy the latest release",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.PENDING_APPROVAL,
            created_at=1700000000,
            updated_at=1700000000,
            assigned_agent_id=uuid4(),
            pending_approval_from_user_id=approver_id,
        )
        assert ticket.status == TicketStatus.PENDING_APPROVAL
        assert ticket.pending_approval_from_user_id == approver_id


class TestNegotiation:
    def test_agent_to_agent(self) -> None:
        negotiation = Negotiation(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.SUBMITTED,
            message="Detected recurring OOM errors in the web app",
            created_at=1700000000,
            from_agent_id=uuid4(),
            to_agent_id=uuid4(),
        )
        assert negotiation.from_user_id is None
        assert negotiation.to_user_id is None

    def test_agent_to_human(self) -> None:
        negotiation = Negotiation(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.APPROVAL_REQUESTED,
            message="PR #42 is ready for merge. Requesting approval.",
            created_at=1700000000,
            from_agent_id=uuid4(),
            to_user_id=uuid4(),
            metadata={"pr_url": "https://github.com/acme/app/pull/42"},
        )
        assert negotiation.to_agent_id is None
        assert negotiation.metadata["pr_url"] == "https://github.com/acme/app/pull/42"

    def test_human_to_agent(self) -> None:
        negotiation = Negotiation(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.APPROVED,
            message="Looks good, approved for merge.",
            created_at=1700000000,
            from_user_id=uuid4(),
            to_agent_id=uuid4(),
        )
        assert negotiation.from_agent_id is None

    def test_metadata_defaults_to_empty_dict(self) -> None:
        n1 = Negotiation(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.ACCEPTED,
            message="Accepted",
            created_at=1700000000,
            from_agent_id=uuid4(),
            to_agent_id=uuid4(),
        )
        n2 = Negotiation(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.ACCEPTED,
            message="Accepted",
            created_at=1700000000,
            from_agent_id=uuid4(),
            to_agent_id=uuid4(),
        )
        assert n1.metadata is not n2.metadata


class TestTicketHistory:
    def test_create_agent_action(self) -> None:
        history = TicketHistory(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            field_changed="status",
            created_at=1700000000,
            actor_agent_id=uuid4(),
            old_value="open",
            new_value="triaging",
        )
        assert history.actor_user_id is None

    def test_create_human_action(self) -> None:
        history = TicketHistory(
            id=uuid4(),
            tenant_id=uuid4(),
            ticket_id=uuid4(),
            field_changed="status",
            created_at=1700000000,
            actor_user_id=uuid4(),
            old_value="pending_approval",
            new_value="resolved",
        )
        assert history.actor_agent_id is None
