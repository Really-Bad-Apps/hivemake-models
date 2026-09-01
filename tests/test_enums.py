from hivemake_models.enums import (
    AgentStatus,
    HiveMemberRole,
    HiveStatus,
    InviteStatus,
    NegotiationAction,
    ProjectStatus,
    TERMINAL_STATUSES,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserStatus,
    WaitingParty,
    waiting_party,
)


class TestHiveStatus:
    def test_values(self) -> None:
        assert HiveStatus.ACTIVE == "active"
        assert HiveStatus.SUSPENDED == "suspended"
        assert HiveStatus.DELETED == "deleted"

    def test_member_count(self) -> None:
        assert len(HiveStatus) == 3


class TestHiveMemberRole:
    def test_values(self) -> None:
        assert HiveMemberRole.OWNER == "owner"
        assert HiveMemberRole.ADMIN == "admin"
        assert HiveMemberRole.MEMBER == "member"

    def test_member_count(self) -> None:
        assert len(HiveMemberRole) == 3


class TestUserStatus:
    def test_values(self) -> None:
        assert UserStatus.ACTIVE == "active"
        assert UserStatus.DISABLED == "disabled"

    def test_member_count(self) -> None:
        assert len(UserStatus) == 2


class TestProjectStatus:
    def test_values(self) -> None:
        assert ProjectStatus.ACTIVE == "active"
        assert ProjectStatus.ARCHIVED == "archived"

    def test_member_count(self) -> None:
        assert len(ProjectStatus) == 2


class TestAgentStatus:
    def test_values(self) -> None:
        assert AgentStatus.ACTIVE == "active"
        assert AgentStatus.PAUSED == "paused"
        assert AgentStatus.DISABLED == "disabled"

    def test_member_count(self) -> None:
        assert len(AgentStatus) == 3


class TestTicketType:
    def test_values(self) -> None:
        assert TicketType.BUG == "bug"
        assert TicketType.FEATURE_REQUEST == "feature_request"
        assert TicketType.TASK == "task"

    def test_member_count(self) -> None:
        assert len(TicketType) == 3


class TestTicketPriority:
    def test_values(self) -> None:
        assert TicketPriority.CRITICAL == "critical"
        assert TicketPriority.HIGH == "high"
        assert TicketPriority.MEDIUM == "medium"
        assert TicketPriority.LOW == "low"

    def test_member_count(self) -> None:
        assert len(TicketPriority) == 4


class TestTicketStatus:
    def test_values(self) -> None:
        assert TicketStatus.OPEN == "open"
        assert TicketStatus.ACCEPTED == "accepted"
        assert TicketStatus.IN_PROGRESS == "in_progress"
        assert TicketStatus.INFO_REQUESTED == "info_requested"
        assert TicketStatus.ESCALATED == "escalated"
        assert TicketStatus.RESOLVED == "resolved"
        assert TicketStatus.CLOSED == "closed"
        assert TicketStatus.WITHDRAWN == "withdrawn"
        assert TicketStatus.REJECTED == "rejected"

    def test_member_count(self) -> None:
        assert len(TicketStatus) == 9


class TestNegotiationAction:
    def test_values(self) -> None:
        assert NegotiationAction.SUBMITTED == "submitted"
        assert NegotiationAction.ACCEPTED == "accepted"
        assert NegotiationAction.REJECTED == "rejected"
        assert NegotiationAction.REDIRECTED == "redirected"
        assert NegotiationAction.INFO_REQUESTED == "info_requested"
        assert NegotiationAction.INFO_PROVIDED == "info_provided"
        assert NegotiationAction.RESOLVED == "resolved"
        assert NegotiationAction.REOPENED == "reopened"
        assert NegotiationAction.CLOSED == "closed"
        assert NegotiationAction.WITHDRAWN == "withdrawn"
        assert NegotiationAction.ESCALATED == "escalated"
        assert NegotiationAction.NOTE == "note"

    def test_member_count(self) -> None:
        assert len(NegotiationAction) == 12


class TestInviteStatus:
    def test_values(self) -> None:
        assert InviteStatus.PENDING == "pending"
        assert InviteStatus.ACCEPTED == "accepted"
        assert InviteStatus.REVOKED == "revoked"
        assert InviteStatus.EXPIRED == "expired"

    def test_member_count(self) -> None:
        assert len(InviteStatus) == 4


class TestEnumsAreStrEnum:
    """All enums should be StrEnum so they serialize as strings."""

    def test_hive_status_is_string(self) -> None:
        assert isinstance(HiveStatus.ACTIVE, str)

    def test_negotiation_action_is_string(self) -> None:
        assert isinstance(NegotiationAction.SUBMITTED, str)

    def test_ticket_status_is_string(self) -> None:
        assert isinstance(TicketStatus.OPEN, str)


class TestWaitingParty:
    """The whose-turn-is-it dimension. Ticket 7976e6fc: rendering only the
    assignment pointed hive managers at the one party that couldn't act."""

    def test_info_requested_waits_on_creator_not_assignee(self) -> None:
        """The regression. `provide_info` is creator-only, and every
        state-changing action errors for the assignee from this status."""
        assert waiting_party(TicketStatus.INFO_REQUESTED) is WaitingParty.CREATOR

    def test_escalated_waits_on_human(self) -> None:
        assert waiting_party(TicketStatus.ESCALATED) is WaitingParty.HUMAN

    def test_terminal_statuses_wait_on_nobody(self) -> None:
        for status in TERMINAL_STATUSES:
            assert waiting_party(status) is WaitingParty.NOBODY

    def test_working_statuses_wait_on_assignee(self) -> None:
        for status in (
            TicketStatus.OPEN,
            TicketStatus.ACCEPTED,
            TicketStatus.IN_PROGRESS,
        ):
            assert waiting_party(status) is WaitingParty.ASSIGNEE

    def test_every_status_is_mapped(self) -> None:
        """FORWARD GUARD, not a regression test — it passes today and exists
        to fail LATER. Adding a status to TicketStatus without deciding whose
        turn it is must break here, loudly, rather than silently defaulting to
        ASSIGNEE on every UI surface."""
        for status in TicketStatus:
            assert isinstance(waiting_party(status), WaitingParty)

    def test_accepts_raw_strings(self) -> None:
        """`Ticket.status` is typed TicketStatus but holds a plain str at
        runtime (psycopg2 rows are splatted in unconverted). The queue
        endpoint passes that value straight in, so a version of this
        function that compared with `is` returned the fallback for every
        real ticket while every enum-constructed test still passed."""
        assert waiting_party("info_requested") is WaitingParty.CREATOR
        assert waiting_party("resolved") is WaitingParty.NOBODY
        assert waiting_party("open") is WaitingParty.ASSIGNEE
