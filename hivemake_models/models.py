from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from hivemake_models.enums import (
    AgentStatus,
    HiveMemberRole,
    HiveStatus,
    HiveVisibility,
    InviteStatus,
    NegotiationAction,
    NotificationTargetKind,
    ProjectStatus,
    TicketPriority,
    TicketStatus,
    TicketType,
    UserStatus,
)


@dataclass
class Hive:
    id: UUID
    name: str
    slug: str
    status: HiveStatus
    created_at: int
    updated_at: int
    visibility: HiveVisibility = HiveVisibility.CLOSED
    # Set when the hive was suspended for having no reachable owner (its
    # sole owner was deleted upstream in Aegis and no admin existed to
    # promote). The hive-purge task hard-deletes suspended hives once
    # this is older than the grace period. NULL for hives suspended for
    # any other reason, and for every active hive.
    suspended_at: Optional[int] = None


@dataclass
class User:
    """Global user record. One row per Aegis identity, regardless of hive count."""
    id: UUID
    email: str
    display_name: str
    status: UserStatus
    created_at: int
    updated_at: int
    aegis_uuid: Optional[UUID] = None
    telegram_chat_id: Optional[str] = None


@dataclass
class HiveMember:
    """Junction row — which user belongs to which hive, and with what role."""
    user_id: UUID
    hive_id: UUID
    role: HiveMemberRole
    created_at: int


@dataclass
class ApiKey:
    """Project-scoped. The key authenticates as the project's agent."""
    id: UUID
    project_id: UUID
    name: str
    key_prefix: str
    key_hash: str
    created_by_user_id: UUID
    created_at: int
    updated_at: int
    expires_at: Optional[int] = None
    revoked_at: Optional[int] = None
    revoked_by_user_id: Optional[UUID] = None
    last_used_at: Optional[int] = None


@dataclass
class Project:
    id: UUID
    hive_id: UUID
    name: str
    slug: str
    status: ProjectStatus
    created_at: int
    updated_at: int
    description: Optional[str] = None


@dataclass
class Agent:
    id: UUID
    hive_id: UUID
    project_id: UUID
    name: str
    status: AgentStatus
    created_at: int
    updated_at: int
    description: Optional[str] = None
    config: dict = field(default_factory=dict)
    registered_at: Optional[int] = None
    autonomous: bool = False


@dataclass
class AgentMatch:
    """One semantic-discovery hit. Score is cosine similarity in [-1, 1];
    1.0 = identical direction (best match). Returned by discover ordered by
    descending score. The agent's own row is excluded by the discover
    service, not by this model."""
    agent_id: UUID
    project_id: UUID
    name: str
    description: str
    score: float


@dataclass
class DiscoverAgentsResult:
    """Result of `discover_agents` — wraps matches with diagnostic counters
    so callers can pinpoint why `matches` is empty without guessing.

    Failure-mode taxonomy (each bullet includes the `matches == []`
    umbrella explicitly — the counters alone aren't enough to choose a
    bucket because the same counter combination can describe a
    successful search too):

      - alone_or_visibility_blocked: `matches == []` AND
        `visible_hive_count == 1` AND `pool_size == 0`. EITHER no
        registered peers exist in the caller's own hive yet, OR the
        caller's hive can't see any cross-hive peers (the relevant
        hives aren't `owner_scope` / `open` for this caller). The
        response can't disambiguate these two — talk to the hive owner.
      - no_candidates: `matches == []` AND `visible_hive_count > 1` AND
        `pool_size == 0`. Visible hives exist but contain no registered
        (non-caller) agents.
      - threshold_filtered: `matches == []` AND `pool_size > 0` AND
        `threshold_dropped > 0`. Every candidate that made the
        top-`limit` slice by similarity scored below `threshold_used`.
        Lower `min_score` and retry — the new floor will recover up to
        `threshold_dropped` more matches.
      - pool_exists_but_query_misses: `matches == []` AND `pool_size > 0`
        AND `threshold_dropped == 0`. Agents exist but none of them
        landed in the top-`limit` AT ALL — the query embedding didn't
        match anyone well. Rephrase the query, not the threshold.

    Note that the same counter shapes can describe non-empty success
    paths: e.g. `pool_size > 0 AND threshold_dropped > 0 AND len(matches) > 0`
    is a routine result where the top-`limit` slice straddled the floor
    (some passed, some didn't). The buckets above only diagnose the
    empty-matches case.

    Field semantics:
      - `pool_size`: registered, non-caller agents across every hive
        the caller can see. Independent of `limit`, `min_score`, and the
        query embedding — same for any query at a given moment.
      - `threshold_dropped`: of the top-`limit` slice by similarity, how
        many fell below `threshold_used`. The directly-actionable
        counter: >0 means a lower `min_score` would recover that many
        more matches; 0 means the threshold isn't the bottleneck.
        Capped at `limit` — if more than `limit` agents would fall
        below the floor, only those that displaced into the top-`limit`
        slice are counted.
      - `threshold_used`: the floor that was applied (server default
        when caller passed `min_score=None`, otherwise the caller's
        value).
      - `visible_hive_count`: hives the caller can see; always >=1
        because the caller's own hive is always visible.

    Note that `pool_size > len(matches)` does NOT prove the threshold
    dropped someone. `limit` also caps `matches` — `threshold_dropped`
    is the specific number that tells you about threshold effects."""
    matches: list[AgentMatch]
    pool_size: int
    threshold_dropped: int
    threshold_used: float
    visible_hive_count: int


@dataclass
class Ticket:
    id: UUID
    hive_id: UUID
    project_id: UUID
    created_by_agent_id: UUID
    ticket_type: TicketType
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    created_at: int
    updated_at: int
    requested_by_user_id: Optional[UUID] = None
    assigned_agent_id: Optional[UUID] = None
    resolution: Optional[str] = None


@dataclass
class OutboundTicket:
    """A Ticket paired with a hint about whether the agent the caller
    is now waiting on is autonomous. Returned by outbound-flavored
    tools (`file_ticket`, `redirect`, `request_info`, `reopen`,
    `list_outbox`) so the caller can decide whether to start polling
    `get_ticket` immediately or wait for a human to drive the other
    side.

    `waiting_on_autonomous` describes THE NEXT RESPONDER, which is
    tool-dependent:
      - file_ticket / redirect / reopen / list_outbox → the assignee.
      - request_info → the creator (the caller is the assignee, and
        after request_info the ticket is waiting on the creator to
        provide_info).

    The value is denormalized from that agent's `Agent.autonomous`
    flag at read time — it's a snapshot, not a live signal. If the
    flag flips between the response and a later poll, the caller sees
    the new value on the next outbound call.
    """
    ticket: Ticket
    waiting_on_autonomous: bool


@dataclass
class TicketListResult:
    """Return shape for `list_inbox`.

    Wraps the ticket list with an overflow guard so an agent asking
    a broad question can be told to narrow down instead of receiving
    a payload that would blow the LLM tool-result cap.

    `too_many` is True when the underlying query would have matched
    more than the server's row-count ceiling. In that case `tickets`
    is empty and `message` carries an advisory suggesting the caller
    supply the `q` filter param. `count` is always the true match count
    (not `len(tickets)`) so the caller can size their next attempt.
    """
    tickets: list[Ticket] = field(default_factory=list)
    too_many: bool = False
    count: int = 0
    message: Optional[str] = None


@dataclass
class UnreadTicket:
    """A terminal ticket the calling agent is a party to and has not read
    since the last thing that happened on it.

    "Read" is per-agent, deliberately NOT a ticket status: both parties see
    the same status but track attention independently, so it cannot live on
    the ticket row. See `TicketReadRepository`.

    Unread itself is derived by COUNTING peer-authored negotiations, not by
    comparing timestamps: `negotiations.created_at` is second-granular with
    a UUID pkey, so same-second actions are unorderable and a timestamp
    comparison would resolve the tie as "read" — silently dropping the
    peer's message. See `TicketReadRepository`.

    `last_activity_at` is therefore presentational only: it orders the list
    most-recent-first and tells the agent how stale the item is. It plays no
    part in deciding what is unread.

    `is_creator` says which side the caller is on, so the agent can tell
    "the thing I asked for was answered" from "the thing I was working on
    was withdrawn" without re-deriving it from the ticket.
    """
    ticket: Ticket
    last_activity_at: int
    is_creator: bool


@dataclass
class CheckTicketsResult:
    """Return shape for `check_tickets` — everything wanting the agent's
    attention, in one call.

    Two buckets, because they answer different questions:
      - `inbox`  — active tickets assigned to the caller (work owed).
      - `unread` — terminal tickets the caller is a party to that moved
        since they last looked (correspondence owed). This is the bucket
        `list_outbox` structurally cannot show: it filters terminal by
        default, so a resolution vanishes the instant it is written.

    Overflow guard matches `TicketListResult`, but is applied to the
    COMBINED result: `count` is the total across both buckets and, on
    `too_many`, BOTH lists are empty. Returning one bucket and suppressing
    the other would quietly answer half the question the agent asked.
    """
    inbox: list[Ticket] = field(default_factory=list)
    unread: list[UnreadTicket] = field(default_factory=list)
    too_many: bool = False
    count: int = 0
    message: Optional[str] = None


@dataclass
class OutboundTicketListResult:
    """Return shape for `list_outbox`. Same overflow-guard contract as
    `TicketListResult`, but each row carries an OutboundTicket (ticket
    + `waiting_on_autonomous` polling hint) rather than a bare Ticket.
    """
    tickets: list[OutboundTicket] = field(default_factory=list)
    too_many: bool = False
    count: int = 0
    message: Optional[str] = None


@dataclass
class Negotiation:
    id: UUID
    hive_id: UUID
    ticket_id: UUID
    action: NegotiationAction
    message: str
    created_at: int
    from_agent_id: Optional[UUID] = None
    from_user_id: Optional[UUID] = None
    to_agent_id: Optional[UUID] = None
    to_user_id: Optional[UUID] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class EscalationActor:
    """Who is acting on an escalated ticket — a human user (via Aegis) or an
    agent (via API key). Used by the escalation-recovery endpoints where a
    hive member resolves/rejects/redirects/provides_info on an escalated
    ticket on the original assignee's behalf. Exactly one of agent_id /
    user_id is set; the service that consumes it enforces that invariant."""
    agent_id: Optional[UUID] = None
    user_id: Optional[UUID] = None


@dataclass
class TicketHistory:
    id: UUID
    hive_id: UUID
    ticket_id: UUID
    field_changed: str
    created_at: int
    actor_agent_id: Optional[UUID] = None
    actor_user_id: Optional[UUID] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class Invite:
    id: UUID
    hive_id: UUID
    email: str
    role: HiveMemberRole
    token: str
    status: InviteStatus
    created_by_user_id: UUID
    expires_at: int
    created_at: int
    updated_at: int
    accepted_at: Optional[int] = None
    accepted_by_aegis_uuid: Optional[UUID] = None


@dataclass
class NotificationTarget:
    """
    A single Telegram destination: a chat, optionally narrowed to a
    supergroup topic. chat_id is a string to match how chat ids are stored
    elsewhere and the byteforge-telegram send API (which takes a str
    chat_id), sidestepping int64 precision concerns.

    This was originally source-agnostic — the dispatcher didn't care where a
    target came from. Escalation action buttons ended that: a keyboard may
    only be attached to a `USER_DM`, since authorizing a button press means
    mapping the clicking Telegram user back to a HiveMake user, and that
    mapping exists only for DMs. `kind` is the discriminator that lets the
    notifier make that call without re-deriving provenance from the chat_id.

    `user_id` is populated for `USER_DM` only, and is the HiveMake user (not
    the Telegram user). It is not needed to authorize a click — the callback
    handler re-resolves the clicker from `callback_query.from.id`, because
    the person who taps need not be the person who was DMed. It is carried
    for logging and for future per-recipient behaviour.

    Defaults keep every existing construction site valid: an unlabelled
    target is a HIVE_CHANNEL, which is the conservative choice — it never
    gets a keyboard.
    """
    chat_id: str
    topic_id: Optional[int] = None
    kind: NotificationTargetKind = NotificationTargetKind.HIVE_CHANNEL
    user_id: Optional[UUID] = None


@dataclass
class HiveTelegramSubscription:
    """One Telegram destination a hive's activity feed fans out to. A hive
    may have many (chat_id, topic_id) pairs; each row can be toggled off
    without deleting it."""
    id: UUID
    hive_id: UUID
    chat_id: str
    created_at: int
    topic_id: Optional[int] = None
    label: Optional[str] = None
    enabled: bool = True


@dataclass
class HiveTelegramLinkToken:
    """Single-use, short-TTL code minted when an admin subscribes a hive to
    Telegram. Consumed by the bot's /link_hive <code> command, which reads
    the chat_id + topic_id from the message metadata."""
    token: str
    hive_id: UUID
    created_by: UUID
    created_at: int
    expires_at: int


@dataclass
class UserTelegramLinkToken:
    """One-time deep-link token binding a user to their Telegram DM chat.
    Embedded in t.me/<bot>?start=link_<token> and consumed by the bot's
    /start link_<token> handler."""
    token: str
    user_id: UUID
    created_at: int
    expires_at: int
