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


# The statuses a ticket cannot leave on its own. RESOLVED is included even
# though it is only SOFT-terminal (the creator may `reopen`): "terminal"
# here means "no longer in either party's working list", which is exactly
# the property the unread machinery keys on.
#
# ESCALATED is deliberately NOT terminal — it is parked with a human and
# still moving. It is also absent from the agent-facing active set, so it
# belongs to neither; that is intentional and matches the inbox default.
TERMINAL_STATUSES: frozenset[TicketStatus] = frozenset({
    TicketStatus.RESOLVED,
    TicketStatus.CLOSED,
    TicketStatus.REJECTED,
    TicketStatus.WITHDRAWN,
})

# The agent-facing "still my problem" set — what `list_inbox` / `list_outbox`
# return by default, and the inbox half of `check_tickets`.
#
# ESCALATED is absent deliberately: an escalated ticket is parked with a
# human, so surfacing it in the agent's working list would be noise the
# agent cannot act on. It reappears once a human recovers it to ACCEPTED.
#
# INFO_REQUESTED is present on BOTH sides on purpose (bug T-805fa610): the
# creator needs to see that a question is waiting on them, and the assignee
# needs to see the ticket is paused pending that answer.
#
# NOT the same as the cross-hive debug view's active set in
# `blueprints/tickets_queue.py`, which deliberately includes TRIAGING,
# IN_PROGRESS and ESCALATED — a stuck escalation is exactly what a human
# staring at that page is looking for. Different audience, different set;
# don't unify them.
AGENT_ACTIVE_STATUSES: frozenset[TicketStatus] = frozenset({
    TicketStatus.OPEN,
    TicketStatus.ACCEPTED,
    TicketStatus.INFO_REQUESTED,
})


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
    # NOTE is a state-neutral message: the ticket's creator or current
    # assignee can append context to the negotiation thread without a
    # status transition. Fills the "actually change of plan, do X"
    # gap where the state machine gives no fitting action to write
    # under (provide_info misrepresents unsolicited context as an
    # answer to a request that never happened).
    NOTE = "note"


class InviteStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"
