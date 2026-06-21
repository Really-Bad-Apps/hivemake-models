from enum import StrEnum


class HiveStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class HiveMemberRole(StrEnum):
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
    INFO_REQUESTED = "info_requested"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"


class NegotiationAction(StrEnum):
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REDIRECTED = "redirected"
    INFO_REQUESTED = "info_requested"
    INFO_PROVIDED = "info_provided"
    RESOLVED = "resolved"
    REOPENED = "reopened"
    CLOSED = "closed"
    WITHDRAWN = "withdrawn"
    ESCALATED = "escalated"


class LearningCategory(StrEnum):
    ROUTING = "routing"
    ERROR_PATTERN = "error_pattern"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


class InviteStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"
