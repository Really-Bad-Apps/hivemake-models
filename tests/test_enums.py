from hivemake_models.enums import (
    AgentStatus,
    HiveMemberRole,
    HiveStatus,
    InviteStatus,
    LearningCategory,
    NegotiationAction,
    ProjectStatus,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserStatus,
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
        assert TicketStatus.TRIAGING == "triaging"
        assert TicketStatus.ACCEPTED == "accepted"
        assert TicketStatus.IN_PROGRESS == "in_progress"
        assert TicketStatus.INFO_REQUESTED == "info_requested"
        assert TicketStatus.ESCALATED == "escalated"
        assert TicketStatus.RESOLVED == "resolved"
        assert TicketStatus.CLOSED == "closed"
        assert TicketStatus.WITHDRAWN == "withdrawn"
        assert TicketStatus.REJECTED == "rejected"

    def test_member_count(self) -> None:
        assert len(TicketStatus) == 10


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


class TestLearningCategory:
    def test_values(self) -> None:
        assert LearningCategory.ROUTING == "routing"
        assert LearningCategory.ERROR_PATTERN == "error_pattern"
        assert LearningCategory.DOMAIN_KNOWLEDGE == "domain_knowledge"

    def test_member_count(self) -> None:
        assert len(LearningCategory) == 3


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
