from uuid import uuid4

from hivemake_models.enums import (
    AgentStatus,
    InviteStatus,
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
    ApiKey,
    Invite,
    Negotiation,
    Project,
    Tenant,
    Ticket,
    TicketHistory,
    User,
)


class TestTenant:
    def test_create(self) -> None:
        tenant = Tenant(
            id=uuid4(),
            name="Acme Corp",
            slug="acme-corp",
            status=TenantStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert tenant.name == "Acme Corp"
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.status == "active"
        assert tenant.notifications_channel_id is None

    def test_create_with_notifications_channel(self) -> None:
        tenant = Tenant(
            id=uuid4(),
            name="Acme Corp",
            slug="acme-corp",
            status=TenantStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            notifications_channel_id="-1001234567890",
        )
        assert tenant.notifications_channel_id == "-1001234567890"


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
        assert user.telegram_chat_id is None

    def test_create_with_telegram(self) -> None:
        user = User(
            id=uuid4(),
            tenant_id=uuid4(),
            aegis_user_id=42,
            email="jason@acme.com",
            display_name="Jason",
            role=UserRole.OWNER,
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            telegram_chat_id="123456789",
        )
        assert user.telegram_chat_id == "123456789"


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


class TestApiKey:
    def test_create_minimal(self) -> None:
        key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            name="prod",
            key_prefix="hmk_live_7Kq2…abcd",
            key_hash="a" * 64,
            created_by_user_id=uuid4(),
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert key.expires_at is None
        assert key.revoked_at is None
        assert key.revoked_by_user_id is None
        assert key.last_used_at is None

    def test_create_with_expiry(self) -> None:
        key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            name="contractor-q2",
            key_prefix="hmk_live_9Zf1…wxyz",
            key_hash="b" * 64,
            created_by_user_id=uuid4(),
            created_at=1700000000,
            updated_at=1700000000,
            expires_at=1710000000,
        )
        assert key.expires_at == 1710000000

    def test_revoked_key(self) -> None:
        revoker_id = uuid4()
        key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            name="old-ci",
            key_prefix="hmk_live_3Aa2…defg",
            key_hash="c" * 64,
            created_by_user_id=uuid4(),
            created_at=1700000000,
            updated_at=1700000100,
            revoked_at=1700000100,
            revoked_by_user_id=revoker_id,
        )
        assert key.revoked_at == 1700000100
        assert key.revoked_by_user_id == revoker_id


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


class TestInvite:
    def test_create_minimal(self) -> None:
        invite = Invite(
            id=uuid4(),
            tenant_id=uuid4(),
            email="alice@acme.com",
            role=UserRole.MEMBER,
            token="opaque-token-abc",
            status=InviteStatus.PENDING,
            created_by_user_id=uuid4(),
            expires_at=1700000000 + 7 * 24 * 60 * 60,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert invite.status == InviteStatus.PENDING
        assert invite.accepted_at is None
        assert invite.accepted_by_aegis_user_id is None

    def test_create_accepted(self) -> None:
        invite = Invite(
            id=uuid4(),
            tenant_id=uuid4(),
            email="bob@acme.com",
            role=UserRole.ADMIN,
            token="opaque-token-xyz",
            status=InviteStatus.ACCEPTED,
            created_by_user_id=uuid4(),
            expires_at=1700000000 + 7 * 24 * 60 * 60,
            created_at=1700000000,
            updated_at=1700000050,
            accepted_at=1700000050,
            accepted_by_aegis_user_id=42,
        )
        assert invite.status == InviteStatus.ACCEPTED
        assert invite.accepted_by_aegis_user_id == 42
