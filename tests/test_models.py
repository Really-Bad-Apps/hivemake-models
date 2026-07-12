from uuid import UUID, uuid4

from hivemake_models.enums import (
    AgentStatus,
    HiveMemberRole,
    HiveStatus,
    HiveVisibility,
    InviteStatus,
    LearningCategory,
    NegotiationAction,
    ProjectStatus,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserStatus,
)
from hivemake_models.models import (
    Agent,
    AgentLearning,
    AgentMatch,
    ApiKey,
    EscalationActor,
    Hive,
    HiveMember,
    HiveTelegramLinkToken,
    HiveTelegramSubscription,
    Invite,
    Negotiation,
    NotificationTarget,
    Project,
    Ticket,
    TicketHistory,
    User,
    UserTelegramLinkToken,
)


class TestHive:
    def test_create(self) -> None:
        hive = Hive(
            id=uuid4(),
            name="Acme Corp",
            slug="acme-corp",
            status=HiveStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert hive.name == "Acme Corp"
        assert hive.status == HiveStatus.ACTIVE
        assert hive.status == "active"
        # Safe default: a brand-new Hive is invisible to the rest of
        # the network until its owner explicitly opens it up.
        assert hive.visibility == HiveVisibility.CLOSED

    def test_create_with_visibility(self) -> None:
        hive = Hive(
            id=uuid4(),
            name="Acme Public",
            slug="acme-public",
            status=HiveStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            visibility=HiveVisibility.OPEN,
        )
        assert hive.visibility == HiveVisibility.OPEN
        assert hive.visibility == "open"


class TestUser:
    def test_create(self) -> None:
        user = User(
            id=uuid4(),
            aegis_user_id=42,
            email="jason@acme.com",
            display_name="Jason",
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert user.aegis_user_id == 42
        assert user.email == "jason@acme.com"
        assert user.telegram_chat_id is None

    def test_create_with_telegram(self) -> None:
        user = User(
            id=uuid4(),
            aegis_user_id=42,
            email="jason@acme.com",
            display_name="Jason",
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            telegram_chat_id="123456789",
        )
        assert user.telegram_chat_id == "123456789"

    def test_aegis_uuid_defaults_to_none(self) -> None:
        user = User(
            id=uuid4(),
            aegis_user_id=42,
            email="jason@acme.com",
            display_name="Jason",
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert user.aegis_uuid is None

    def test_create_with_aegis_uuid(self) -> None:
        user = User(
            id=uuid4(),
            aegis_user_id=42,
            email="jason@acme.com",
            display_name="Jason",
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            aegis_uuid=UUID("9b2c7a4d-1234-5678-9abc-def012345678"),
        )
        assert user.aegis_uuid == UUID("9b2c7a4d-1234-5678-9abc-def012345678")


class TestHiveMember:
    def test_create(self) -> None:
        user_id = uuid4()
        hive_id = uuid4()
        member = HiveMember(
            user_id=user_id,
            hive_id=hive_id,
            role=HiveMemberRole.OWNER,
            created_at=1700000000,
        )
        assert member.user_id == user_id
        assert member.hive_id == hive_id
        assert member.role == HiveMemberRole.OWNER
        assert member.role == "owner"

    def test_admin_role(self) -> None:
        member = HiveMember(
            user_id=uuid4(),
            hive_id=uuid4(),
            role=HiveMemberRole.ADMIN,
            created_at=1700000000,
        )
        assert member.role == HiveMemberRole.ADMIN


class TestProject:
    def test_create_with_description(self) -> None:
        project = Project(
            id=uuid4(),
            hive_id=uuid4(),
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
            hive_id=uuid4(),
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
            hive_id=uuid4(),
            project_id=uuid4(),
            name="App Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert agent.config == {}
        assert agent.description is None

    def test_create_with_config(self) -> None:
        config = {"redirect_rules": {"max_redirects": 3}}
        agent = Agent(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            name="App Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            config=config,
        )
        assert agent.config["redirect_rules"]["max_redirects"] == 3

    def test_default_registered_at_is_none(self) -> None:
        agent = Agent(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            name="Ghost Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert agent.registered_at is None

    def test_registered_at_set(self) -> None:
        agent = Agent(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            name="Registered Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000005,
            registered_at=1700000005,
        )
        assert agent.registered_at == 1700000005


class TestAgentMatch:
    def test_create(self) -> None:
        match = AgentMatch(
            agent_id=uuid4(),
            project_id=uuid4(),
            name="Boudica",
            description="Frontend release engineer",
            score=0.82,
        )
        assert match.name == "Boudica"
        assert match.score == 0.82

    def test_score_zero(self) -> None:
        match = AgentMatch(
            agent_id=uuid4(),
            project_id=uuid4(),
            name="Argus",
            description="Log watcher",
            score=0.0,
        )
        assert match.score == 0.0


class TestApiKey:
    def test_create_minimal(self) -> None:
        key = ApiKey(
            id=uuid4(),
            project_id=uuid4(),
            name="prod",
            key_prefix="hm_authsvc_3kx9",
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
            project_id=uuid4(),
            name="contractor-q2",
            key_prefix="hm_billing_9Zf1",
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
            project_id=uuid4(),
            name="old-ci",
            key_prefix="hm_web_3Aa2",
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
            hive_id=uuid4(),
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
            hive_id=uuid4(),
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
            hive_id=uuid4(),
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
        assert ticket.resolution is None


class TestNegotiation:
    def test_agent_to_agent(self) -> None:
        negotiation = Negotiation(
            id=uuid4(),
            hive_id=uuid4(),
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
            hive_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.ESCALATED,
            message="Stuck on merging PR #42 — need a human to weigh in.",
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
            hive_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.INFO_PROVIDED,
            message="Here's the missing context — proceed.",
            created_at=1700000000,
            from_user_id=uuid4(),
            to_agent_id=uuid4(),
        )
        assert negotiation.from_agent_id is None

    def test_metadata_defaults_to_empty_dict(self) -> None:
        n1 = Negotiation(
            id=uuid4(),
            hive_id=uuid4(),
            ticket_id=uuid4(),
            action=NegotiationAction.ACCEPTED,
            message="Accepted",
            created_at=1700000000,
            from_agent_id=uuid4(),
            to_agent_id=uuid4(),
        )
        n2 = Negotiation(
            id=uuid4(),
            hive_id=uuid4(),
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
            hive_id=uuid4(),
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
            hive_id=uuid4(),
            ticket_id=uuid4(),
            field_changed="status",
            created_at=1700000000,
            actor_user_id=uuid4(),
            old_value="escalated",
            new_value="resolved",
        )
        assert history.actor_agent_id is None


class TestInvite:
    def test_create_minimal(self) -> None:
        invite = Invite(
            id=uuid4(),
            hive_id=uuid4(),
            email="alice@acme.com",
            role=HiveMemberRole.MEMBER,
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
        assert invite.accepted_by_aegis_uuid is None

    def test_create_accepted(self) -> None:
        invite = Invite(
            id=uuid4(),
            hive_id=uuid4(),
            email="bob@acme.com",
            role=HiveMemberRole.ADMIN,
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

    def test_create_accepted_with_aegis_uuid(self) -> None:
        invite = Invite(
            id=uuid4(),
            hive_id=uuid4(),
            email="carol@acme.com",
            role=HiveMemberRole.ADMIN,
            token="opaque-token-qrs",
            status=InviteStatus.ACCEPTED,
            created_by_user_id=uuid4(),
            expires_at=1700000000 + 7 * 24 * 60 * 60,
            created_at=1700000000,
            updated_at=1700000050,
            accepted_at=1700000050,
            accepted_by_aegis_user_id=42,
            accepted_by_aegis_uuid=UUID("9b2c7a4d-1234-5678-9abc-def012345678"),
        )
        assert invite.accepted_by_aegis_uuid == UUID("9b2c7a4d-1234-5678-9abc-def012345678")


class TestNotificationTarget:
    def test_main_feed_default(self) -> None:
        target = NotificationTarget(chat_id="-1001234567890")
        assert target.chat_id == "-1001234567890"
        assert target.topic_id is None

    def test_with_topic(self) -> None:
        target = NotificationTarget(chat_id="-1001234567890", topic_id=42)
        assert target.topic_id == 42


class TestHiveTelegramSubscription:
    def test_create_minimal(self) -> None:
        sub = HiveTelegramSubscription(
            id=uuid4(),
            hive_id=uuid4(),
            chat_id="-1001234567890",
            created_at=1700000000,
        )
        assert sub.topic_id is None
        assert sub.label is None
        assert sub.enabled is True

    def test_create_full(self) -> None:
        sub = HiveTelegramSubscription(
            id=uuid4(),
            hive_id=uuid4(),
            chat_id="-1001234567890",
            created_at=1700000000,
            topic_id=7,
            label="Hive Alpha activity feed",
            enabled=False,
        )
        assert sub.topic_id == 7
        assert sub.label == "Hive Alpha activity feed"
        assert sub.enabled is False


class TestHiveTelegramLinkToken:
    def test_create(self) -> None:
        token = HiveTelegramLinkToken(
            token="abc123",
            hive_id=uuid4(),
            created_by=uuid4(),
            created_at=1700000000,
            expires_at=1700000600,
        )
        assert token.token == "abc123"
        assert token.expires_at - token.created_at == 600


class TestUserTelegramLinkToken:
    def test_create(self) -> None:
        token = UserTelegramLinkToken(
            token="xyz789",
            user_id=uuid4(),
            created_at=1700000000,
            expires_at=1700000600,
        )
        assert token.token == "xyz789"
        assert token.user_id is not None


class TestEscalationActor:
    def test_agent_actor(self) -> None:
        agent_id = uuid4()
        actor = EscalationActor(agent_id=agent_id)
        assert actor.agent_id == agent_id
        assert actor.user_id is None

    def test_user_actor(self) -> None:
        user_id = uuid4()
        actor = EscalationActor(user_id=user_id)
        assert actor.user_id == user_id
        assert actor.agent_id is None

    def test_empty_default(self) -> None:
        actor = EscalationActor()
        assert actor.agent_id is None
        assert actor.user_id is None
