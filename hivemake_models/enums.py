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
# Note that membership here is NOT sufficient to make the creator half
# visible — the query has to ask the creator-side question too. It was in
# this set the whole time `check_tickets` queried only
# `list_by_assigned_agent`, which silently dropped exactly that half. See
# CREATOR_AWAITING_STATUSES below and ticket e5065401.
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

# Statuses where the ticket's CREATOR owes the next move — the
# `awaiting_your_response` bucket of `check_tickets`, queried against
# `created_by_agent_id` rather than `assigned_agent_id`.
#
# Only INFO_REQUESTED qualifies today, and the audit behind ticket e5065401
# checked every (status x party) cell to confirm it is the only one:
#   - OPEN / ACCEPTED     — assignee's move; creator waits, owes nothing.
#   - ESCALATED           — parked with a human. NEITHER agent can act, and
#                           this set is about who owes the next MOVE, so it
#                           correctly does not belong here. It gets its own
#                           bucket instead — see ESCALATED_STATUSES below.
#                           (Until 2026-08-13 it was in no bucket at all and
#                           this comment called that a deliberate permanent
#                           blind spot. That was wrong: "cannot act on it" is
#                           not "should not know about it".)
#   - TERMINAL_STATUSES   — covered by the unread bucket, both parties.
#   - TRIAGING/IN_PROGRESS— unreachable; no transition produces either
#                           (see the INFO_REQUESTED row of the transition
#                           table in ticket_service, which notes the
#                           IN_PROGRESS half is forward-looking).
#
# A single-member frozenset rather than a bare status because the next
# status added here must be added in ONE place. Splitting the creator-side
# set across the service and the blueprint is how the assignee-side set
# drifted in the first place.
CREATOR_AWAITING_STATUSES: frozenset[TicketStatus] = frozenset({
    TicketStatus.INFO_REQUESTED,
})

# The `escalated` bucket of `check_tickets` — tickets parked with a human.
#
# Queried against BOTH `assigned_agent_id` and `created_by_agent_id`,
# because only the assignee can escalate, so the two sides see a given
# ticket for different reasons and neither query alone is complete. Getting
# this half-right is the exact shape of ticket e5065401: a creator-side
# query that was never asked returned a clean "nothing for you".
#
# Deliberately NOT merged into AGENT_ACTIVE_STATUSES. That set answers "who
# owes the next move", and on an escalated ticket the answer is neither
# agent — putting it there would push tickets into `inbox` that the agent
# would then try, and fail, to act on. Separate set, separate bucket,
# read-only.
ESCALATED_STATUSES: frozenset[TicketStatus] = frozenset({
    TicketStatus.ESCALATED,
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


class NotificationTargetKind(StrEnum):
    """Where a Telegram notification target came from.

    `NotificationTarget` was deliberately source-agnostic — the dispatcher
    didn't care. Action buttons break that: a keyboard may only be attached
    to a USER_DM, because authorizing a button press requires mapping the
    clicking Telegram user back to a HiveMake user, and that mapping only
    exists for DMs.

    In a private chat Telegram sets `chat.id == user.id`, so a
    `callback_query`'s `from.id` matches `users.telegram_chat_id` directly.
    A HIVE_CHANNEL has no such mapping: `hive_telegram_subscriptions` stores
    only `(hive_id, chat_id, topic_id)` — no user column, no notion of who
    is in the room. Hence channels stay informational.
    """
    USER_DM = "user_dm"
    HIVE_CHANNEL = "hive_channel"


class InviteStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class WaitingParty(StrEnum):
    """Who owes the next move on a ticket — the whose-turn-is-it dimension,
    which is NOT the same as the assignment dimension.

    Assignment answers "who owns this work"; this answers "who is everyone
    else waiting on". They agree for most of a ticket's life and diverge on
    exactly one status: INFO_REQUESTED, where the assignee asked a question
    and the CREATOR must answer it. Rendering only the assignment there
    points a reader at the one party that cannot act — every state-changing
    action errors for them, `provide_info` included (it is creator-only).

    That divergence is not cosmetic. It cost a hive manager real time
    (ticket 7976e6fc): the UI showed a stuck ticket as "assigned to" the
    agent who had already done everything it could, so there was no way to
    tell which agent needed nudging. Surface this ALONGSIDE the assignee,
    never instead of it — both dimensions are real and a reader needs both.
    """
    ASSIGNEE = "assignee"
    CREATOR = "creator"
    HUMAN = "human"
    NOBODY = "nobody"


def waiting_party(status: TicketStatus) -> WaitingParty:
    """Map a ticket status to the party who owes the next move.

    Lives in models, not in a blueprint or a React helper, because the
    server and the web UI must not drift on this — a second copy is how
    the assignment/turn confusion gets re-introduced on one surface only.

    Exhaustive over TicketStatus deliberately: no fallback branch, so
    adding a status to the enum without deciding whose turn it is fails
    loudly here instead of silently defaulting to ASSIGNEE.

    Coerces first because `Ticket.status` is annotated `TicketStatus` but
    holds a plain `str` at runtime — rows come back from psycopg2 and are
    splatted into the dataclass without conversion. `==` and set membership
    both work on a StrEnum either way; `is` does NOT, and an identity check
    here would return the fallback for every real ticket while passing
    every test that constructs statuses from the enum.
    """
    status = TicketStatus(status)
    if status in TERMINAL_STATUSES:
        # Nobody's turn: the ticket is decided. RESOLVED is soft-terminal
        # (the creator may reopen) but reopening is optional, not owed.
        return WaitingParty.NOBODY
    if status is TicketStatus.INFO_REQUESTED:
        return WaitingParty.CREATOR
    if status is TicketStatus.ESCALATED:
        # Parked with a hive member. Neither agent can act until a human
        # runs one of the four recovery actions.
        return WaitingParty.HUMAN
    if status in (
        TicketStatus.OPEN,
        TicketStatus.TRIAGING,
        TicketStatus.ACCEPTED,
        TicketStatus.IN_PROGRESS,
    ):
        return WaitingParty.ASSIGNEE
    raise ValueError(f"no waiting party defined for status {status!r}")
