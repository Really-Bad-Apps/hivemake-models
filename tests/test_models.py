from uuid import UUID, uuid4

from hivemake_models.enums import (
    AgentStatus,
    HiveMemberRole,
    HiveStatus,
    HiveVisibility,
    InviteStatus,
    NegotiationAction,
    ProjectStatus,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserStatus,
)
from hivemake_models.models import (
    is_self_assigned,
    Agent,
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
    OutboundTicket,
    OutboundTicketListResult,
    Project,
    Ticket,
    TicketHistory,
    TicketListResult,
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
            email="jason@acme.com",
            display_name="Jason",
            status=UserStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert user.email == "jason@acme.com"
        assert user.telegram_chat_id is None

    def test_create_with_telegram(self) -> None:
        user = User(
            id=uuid4(),
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

    def test_default_autonomous_is_false(self) -> None:
        agent = Agent(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            name="Manual Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
        )
        assert agent.autonomous is False

    def test_autonomous_set_true(self) -> None:
        agent = Agent(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            name="Autonomous Agent",
            status=AgentStatus.ACTIVE,
            created_at=1700000000,
            updated_at=1700000000,
            autonomous=True,
        )
        assert agent.autonomous is True


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


class TestOutboundTicket:
    def _sample_ticket(self) -> Ticket:
        return Ticket(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            created_by_agent_id=uuid4(),
            ticket_type=TicketType.TASK,
            title="Deploy something",
            description="Please deploy it",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=1700000000,
            updated_at=1700000000,
        )

    def test_wraps_ticket_with_autonomous_true(self) -> None:
        ticket = self._sample_ticket()
        outbound = OutboundTicket(ticket=ticket, waiting_on_autonomous=True)
        assert outbound.ticket is ticket
        assert outbound.waiting_on_autonomous is True

    def test_wraps_ticket_with_autonomous_false(self) -> None:
        ticket = self._sample_ticket()
        outbound = OutboundTicket(ticket=ticket, waiting_on_autonomous=False)
        assert outbound.waiting_on_autonomous is False


def _sample_ticket() -> Ticket:
    return Ticket(
        id=uuid4(),
        hive_id=uuid4(),
        project_id=uuid4(),
        created_by_agent_id=uuid4(),
        ticket_type=TicketType.TASK,
        title="Deploy something",
        description="Please deploy it",
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        created_at=1700000000,
        updated_at=1700000000,
    )


class TestTicketListResult:
    def test_default_empty_shape(self) -> None:
        result = TicketListResult()
        assert result.tickets == []
        assert result.too_many is False
        assert result.count == 0
        assert result.message is None

    def test_success_shape(self) -> None:
        tickets = [_sample_ticket(), _sample_ticket()]
        result = TicketListResult(tickets=tickets, too_many=False, count=2)
        assert result.tickets is tickets
        assert result.too_many is False
        assert result.count == 2
        assert result.message is None

    def test_overflow_shape(self) -> None:
        result = TicketListResult(
            tickets=[], too_many=True, count=87, message="Narrow further.",
        )
        assert result.tickets == []
        assert result.too_many is True
        assert result.count == 87
        assert result.message == "Narrow further."


class TestOutboundTicketListResult:
    def test_default_empty_shape(self) -> None:
        result = OutboundTicketListResult()
        assert result.tickets == []
        assert result.too_many is False
        assert result.count == 0
        assert result.message is None

    def test_success_shape(self) -> None:
        outbound = OutboundTicket(ticket=_sample_ticket(), waiting_on_autonomous=True)
        result = OutboundTicketListResult(
            tickets=[outbound], too_many=False, count=1,
        )
        assert result.tickets == [outbound]
        assert result.tickets[0].waiting_on_autonomous is True
        assert result.count == 1

    def test_overflow_shape(self) -> None:
        result = OutboundTicketListResult(
            tickets=[], too_many=True, count=58, message="Provide `q`.",
        )
        assert result.tickets == []
        assert result.too_many is True
        assert result.count == 58
        assert result.message == "Provide `q`."


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
            new_value="accepted",
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
            accepted_by_aegis_uuid=UUID("9b2c7a4d-1234-5678-9abc-def012345678"),
        )
        assert invite.status == InviteStatus.ACCEPTED
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


class TestIsSelfAssigned:
    """The UUID-vs-str comparison here is the whole reason this is a shared
    helper rather than three inline `==` checks."""

    def _ticket(self, created, assigned) -> Ticket:
        return Ticket(
            id=uuid4(),
            hive_id=uuid4(),
            project_id=uuid4(),
            created_by_agent_id=created,
            ticket_type=TicketType.TASK,
            title="t",
            description="d",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            created_at=1700000000,
            updated_at=1700000000,
            assigned_agent_id=assigned,
        )

    def test_same_agent_is_self_assigned(self) -> None:
        agent = uuid4()
        assert is_self_assigned(self._ticket(agent, agent)) is True

    def test_different_agents_is_not(self) -> None:
        assert is_self_assigned(self._ticket(uuid4(), uuid4())) is False

    def test_mixed_uuid_and_str_still_matches(self) -> None:
        """psycopg2 hands these back as `str` unless `register_uuid()` is
        called, which this codebase never does — so a ticket built one way
        and read another must still compare equal. A bare `==` returns False
        here, which would report every self-assigned ticket as ordinary
        work while passing a test that built both sides identically."""
        agent = uuid4()
        assert is_self_assigned(self._ticket(agent, str(agent))) is True
        assert is_self_assigned(self._ticket(str(agent), agent)) is True

    def test_unassigned_ticket_is_not_self_assigned(self) -> None:
        assert is_self_assigned(self._ticket(uuid4(), None)) is False
