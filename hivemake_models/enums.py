from enum import StrEnum


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class UserStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class AgentStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class TicketType(StrEnum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    TASK = "task"


class TicketPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketStatus(StrEnum):
    OPEN = "open"
    TRIAGING = "triaging"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"
    DENIED = "denied"


class NegotiationAction(StrEnum):
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REDIRECTED = "redirected"
    INFO_REQUESTED = "info_requested"
    INFO_PROVIDED = "info_provided"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVED = "approved"
    DENIED = "denied"
    REVISION_REQUESTED = "revision_requested"


class LearningCategory(StrEnum):
    ROUTING = "routing"
    ERROR_PATTERN = "error_pattern"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


class InviteStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"
