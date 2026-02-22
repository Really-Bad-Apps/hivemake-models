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


class TestTenantStatus:
    def test_values(self) -> None:
        assert TenantStatus.ACTIVE == "active"
        assert TenantStatus.SUSPENDED == "suspended"
        assert TenantStatus.DELETED == "deleted"

    def test_member_count(self) -> None:
        assert len(TenantStatus) == 3


class TestUserRole:
    def test_values(self) -> None:
        assert UserRole.OWNER == "owner"
        assert UserRole.ADMIN == "admin"
        assert UserRole.MEMBER == "member"

    def test_member_count(self) -> None:
        assert len(UserRole) == 3


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
        assert TicketStatus.PENDING_APPROVAL == "pending_approval"
        assert TicketStatus.RESOLVED == "resolved"
        assert TicketStatus.CLOSED == "closed"
        assert TicketStatus.REJECTED == "rejected"
        assert TicketStatus.DENIED == "denied"

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
        assert NegotiationAction.APPROVAL_REQUESTED == "approval_requested"
        assert NegotiationAction.APPROVED == "approved"
        assert NegotiationAction.DENIED == "denied"
        assert NegotiationAction.REVISION_REQUESTED == "revision_requested"

    def test_member_count(self) -> None:
        assert len(NegotiationAction) == 10


class TestLearningCategory:
    def test_values(self) -> None:
        assert LearningCategory.ROUTING == "routing"
        assert LearningCategory.ERROR_PATTERN == "error_pattern"
        assert LearningCategory.DOMAIN_KNOWLEDGE == "domain_knowledge"

    def test_member_count(self) -> None:
        assert len(LearningCategory) == 3


class TestEnumsAreStrEnum:
    """All enums should be StrEnum so they serialize as strings."""

    def test_tenant_status_is_string(self) -> None:
        assert isinstance(TenantStatus.ACTIVE, str)

    def test_negotiation_action_is_string(self) -> None:
        assert isinstance(NegotiationAction.SUBMITTED, str)

    def test_ticket_status_is_string(self) -> None:
        assert isinstance(TicketStatus.OPEN, str)
