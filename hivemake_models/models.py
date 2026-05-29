from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

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


@dataclass
class Hive:
    id: UUID
    name: str
    slug: str
    status: HiveStatus
    created_at: int
    updated_at: int


@dataclass
class User:
    """Global user record. One row per Aegis identity, regardless of hive count."""
    id: UUID
    aegis_user_id: int
    email: str
    display_name: str
    status: UserStatus
    created_at: int
    updated_at: int
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


@dataclass
class AgentLearning:
    id: UUID
    hive_id: UUID
    agent_id: UUID
    content: str
    active: bool
    created_at: int
    updated_at: int
    category: Optional[LearningCategory] = None
    source_ticket_id: Optional[UUID] = None


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
    pending_approval_from_agent_id: Optional[UUID] = None
    pending_approval_from_user_id: Optional[UUID] = None
    resolution: Optional[str] = None


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
class ApprovalActor:
    """Who is acting on an approval gate — an agent (via API key) or a human
    user (via Aegis). Exactly one of agent_id / user_id is set; the service
    that consumes it enforces that invariant and matches it against the
    ticket's pending_approval_from_{agent,user}_id."""
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
    accepted_by_aegis_user_id: Optional[int] = None


@dataclass
class NotificationTarget:
    """
    A single Telegram destination: a chat, optionally narrowed to a
    supergroup topic. Source-agnostic by design — the dispatcher doesn't
    care whether the target came from a hive activity-feed subscription or
    from a user's linked DM chat. chat_id is a string to match how chat ids
    are stored elsewhere and the byteforge-telegram send API (which takes a
    str chat_id), sidestepping int64 precision concerns.
    """
    chat_id: str
    topic_id: Optional[int] = None


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
