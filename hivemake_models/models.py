from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

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


@dataclass
class Tenant:
    id: UUID
    aegis_site_id: int
    name: str
    slug: str
    status: TenantStatus
    created_at: int
    updated_at: int


@dataclass
class User:
    id: UUID
    tenant_id: UUID
    aegis_user_id: int
    email: str
    display_name: str
    role: UserRole
    status: UserStatus
    created_at: int
    updated_at: int


@dataclass
class Project:
    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    status: ProjectStatus
    created_at: int
    updated_at: int
    description: Optional[str] = None


@dataclass
class Agent:
    id: UUID
    tenant_id: UUID
    project_id: UUID
    name: str
    status: AgentStatus
    created_at: int
    updated_at: int
    gatekeeper_client_id: Optional[UUID] = None
    description: Optional[str] = None
    config: dict = field(default_factory=dict)


@dataclass
class ProjectDependency:
    id: UUID
    tenant_id: UUID
    project_id: UUID
    depends_on_project_id: UUID
    created_at: int


@dataclass
class AgentLearning:
    id: UUID
    tenant_id: UUID
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
    tenant_id: UUID
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
    tenant_id: UUID
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
class TicketHistory:
    id: UUID
    tenant_id: UUID
    ticket_id: UUID
    field_changed: str
    created_at: int
    actor_agent_id: Optional[UUID] = None
    actor_user_id: Optional[UUID] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
