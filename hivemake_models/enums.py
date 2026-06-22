from enum import StrEnum


class HiveStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class HiveVisibility(StrEnum):
    """Cross-hive routing/discovery axis (Slice 2 of hive-visibility design).

    Same-axis design: routing visibility == discovery visibility. A hive
    that is invisible to a peer is also unroutable from that peer.

    - CLOSED: invisible and unroutable from every other hive. Default.
    - OWNER_SCOPE: visible/routable from other hives owned by the same
      user. Lets a single owner federate their own hives without
      exposing them to the wider org/network.
    - OPEN: visible/routable from any hive. Use only when the hive is
      intended to accept inbound traffic from strangers.

    Slice 2 stores the field; Slice 3 enforces it in discover_agents
    and file_ticket routing.
    """
    CLOSED = "closed"
    OWNER_SCOPE = "owner_scope"
    OPEN = "open"


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
