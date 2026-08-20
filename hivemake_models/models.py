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
class EscalatedTicket:
    """A ticket the calling agent is a party to that is parked with a human.

    Read-only awareness: NEITHER agent can act on an escalated ticket, which
    is why it was originally left out of every `check_tickets` bucket. That
    turned out to be the wrong call — "you cannot act on it" is not the same
    as "you should not know about it". Across sessions an agent loses the
    memory that it escalated something, gets a clean "nothing for you", and
    the work sits. That is the `e5065401` failure shape exactly.

    Note the human-facing queue (`blueprints/tickets_queue.py`) has always
    included ESCALATED, because a stuck escalation is precisely what a human
    scanning that page is looking for. Humans had this visibility and agents
    did not.

    `is_creator` is required rather than derivable: `waiting_on` is "human"
    for BOTH parties here, so it cannot say which side you are on, and
    "did I escalate this, or did someone escalate my ticket" changes what a
    human will ask you about it.
    """
    ticket: Ticket
    is_creator: bool


@dataclass
class TicketDigest:
    """One compact row of the overflow index — see `CheckTicketsResult`.

    Deliberately NOT a Ticket: the whole point is to fit a set that was too
    large to return in full. Carries only what is needed to choose a ticket
    and then `get_ticket` it.

    `bucket` names which list this row WOULD have appeared in, so the agent
    keeps the obligation distinction (work owed vs own backlog vs answer
    owed vs correspondence vs parked) that the buckets exist to draw.
    """
    ticket_id: UUID
    title: str
    status: TicketStatus
    bucket: str


def is_self_assigned(ticket: "Ticket") -> bool:
    """True when a ticket's creator and assignee are the same agent.

    Lives in models for the same reason `waiting_party` does: three
    surfaces ask this question — the ticket service (to refuse
    `request_info`), the activity notifier (to suppress the self-filing
    announcement), and the read path — and a second copy is how they drift.

    Compares STRING forms deliberately. These columns arrive from psycopg2
    and may be `UUID` or `str` depending on the path, and `UUID(...) ==
    str(...)` is False — so an identity-shaped comparison would report
    every self-assigned ticket as ordinary work while passing any test that
    builds both sides the same way. Same trap `waiting_party` documents for
    statuses.

    An unassigned ticket is not self-assigned; the explicit `None` guard
    keeps two null columns from collapsing to `"None" == "None"`.
    """
    if ticket.assigned_agent_id is None or ticket.created_by_agent_id is None:
        return False
    return str(ticket.created_by_agent_id) == str(ticket.assigned_agent_id)


@dataclass
class CheckTicketsResult:
    """Return shape for `check_tickets` — everything wanting the agent's
    attention, in one call.

    Five buckets, because they are five different obligations with five
    different next actions:
      - `inbox` — active tickets assigned to the caller BY SOMEONE ELSE
        (work owed to another agent). The caller can `resolve` / `reject` /
        `request_info` these.
      - `self_assigned` — active tickets the caller both filed AND owns.
        Same verbs as `inbox` minus `request_info`, but a different
        obligation: nobody is blocked on these.
      - `awaiting_your_response` — tickets the caller FILED whose assignee
        called `request_info`. Work is paused until the caller answers, and
        `provide_info` is creator-only, so the caller is the only party who
        can move them.
      - `unread` — terminal tickets the caller is a party to that moved
        since they last looked (correspondence owed). This is the bucket
        `list_outbox` structurally cannot show: it filters terminal by
        default, so a resolution vanishes the instant it is written.

    WHY `awaiting_your_response` IS ITS OWN BUCKET rather than extra rows in
    `inbox`: the two are not the same obligation. `inbox` means "assigned to
    me", and every action available on an inbox row is unavailable on one of
    these (and vice versa). Folding them together would force every caller to
    re-derive which is which from `status` + `created_by_agent_id` per row,
    and any that forgot would reach for `resolve` and get an
    InvalidTransitionError.

    HISTORY — this bucket closes a gap that reopened a fixed bug.
    `INFO_REQUESTED` sits in `AGENT_ACTIVE_STATUSES` for BOTH parties on
    purpose (bug T-805fa610: the creator must see that a question is waiting
    on them), and `list_outbox` honors that. But `check_tickets` built its
    inbox from `list_by_assigned_agent` alone, so the creator half never
    survived the query — and the playbook tells agents to open with
    `check_tickets` INSTEAD of `list_outbox`. Net effect: the one agent who
    could answer got a clean "nothing for you", and tickets rotted until a
    human stumbled on them (ticket e5065401; live case 0bd66d48, found only
    after @jmazzahacks nudged the responder by hand).

      - `escalated` — tickets parked with a human. Read-only awareness; see
        `EscalatedTicket`.

    WHY `self_assigned` IS ITS OWN BUCKET, by the same argument. Agents may
    file tickets against themselves, which is how work survives the end of a
    session: local memory and plan files have no freshness signal and
    nothing pulls them, whereas `check_tickets` is pulled at the start of
    every session by construction.

    But self-assigned work is a THIRD obligation class. An `inbox` row means
    another agent is waiting; a `self_assigned` row means nobody is. Folding
    them together would bury genuine inbound work under the caller's own
    someday-pile and make the playbook's "inbox = work you owe someone"
    framing false. That is the `awaiting_your_response` split again, pointed
    the other way.

    Separating them also makes the overlap dedup STRUCTURAL. A ticket whose
    creator and assignee are the same agent is returned by both the
    assigned-side and created-side queries; routing it to exactly one bucket
    removes the double-count at the source, rather than needing a third
    query to subtract it back out (see `_check_tickets_overflow`, which
    previously tolerated the overcount only because legacy self-routed rows
    were rare).

    Overflow guard matches `TicketListResult`, but is applied to the
    COMBINED result: on `too_many`, ALL bucket lists are empty. Returning
    one bucket and suppressing the others would quietly answer part of the
    question the agent asked.

    `self_assigned` IS EXEMPT FROM THE OVERFLOW TRIGGER, and this is
    load-bearing rather than an optimisation. Were it counted, one grooming
    pass that files more self-tickets than the ceiling would put the agent
    permanently on the degraded path — every later call returning `too_many`
    with `inbox` and `awaiting_your_response` empty, including rows where
    another agent is blocked. The bucket split exists to stop a personal
    backlog burying inbound work; letting that backlog trip the shared
    ceiling would reintroduce the same harm one layer down. So the trigger
    measures obligations involving other parties, and `self_assigned` is
    capped separately with `self_assigned_truncated` reporting the clip.

    `count` still spans all five buckets — it describes the response, not
    the trigger.

    ON OVERFLOW, `digest` IS THE ANSWER. Emptying the buckets was right —
    an undetectable partial answer is worse than none — but for a long time
    it also left the caller with nowhere to go, and the documented recovery
    was `list_inbox` / `list_outbox` with `q=`. That is circular: the
    ceiling created the problem the escape hatch solved, and it is why those
    tools could not be retired.

    So `too_many` no longer means "I refuse". The buckets stay empty (that
    contract is unchanged and still literally true) and `digest` carries a
    compact index of every ticket that would have been in them — id, title,
    status, and which bucket. The caller picks and calls `get_ticket`.

    This is also what replaces keyword search over active tickets: search's
    real job was navigating a list too big to read, and the digest makes the
    whole set visible instead.

    `digest` is EMPTY when `too_many` is False — the buckets already hold
    everything, and duplicating them would just spend tokens.
    """
    inbox: list[Ticket] = field(default_factory=list)
    self_assigned: list[Ticket] = field(default_factory=list)
    self_assigned_truncated: bool = False
    awaiting_your_response: list[Ticket] = field(default_factory=list)
    unread: list[UnreadTicket] = field(default_factory=list)
    escalated: list[EscalatedTicket] = field(default_factory=list)
    too_many: bool = False
    count: int = 0
    message: Optional[str] = None
    digest: list[TicketDigest] = field(default_factory=list)
    digest_truncated: bool = False


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
