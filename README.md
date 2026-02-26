# hivemake-models

Shared data models and enums for [HiveMake.ai](https://hivemake.ai) — a multi-agent ticketing system.

This is a lightweight library with no database dependencies. It defines the common data structures used across all HiveMake repositories.

## Enums

| Enum | Values |
|------|--------|
| `TenantStatus` | active, suspended, deactivated |
| `UserRole` | owner, admin, member |
| `UserStatus` | active, disabled |
| `ProjectStatus` | active, archived |
| `AgentStatus` | active, paused, disabled |
| `TicketType` | bug, feature_request, task, question |
| `TicketPriority` | low, medium, high, critical |
| `TicketStatus` | open, triaging, in_progress, pending_approval, denied, blocked, resolved, closed |
| `NegotiationAction` | redirected, accepted, rejected, escalated, approval_requested, approved, denied, revision_requested |
| `LearningCategory` | routing, error_pattern, domain_knowledge |

## Models

`Tenant`, `User`, `Project`, `Agent`, `ProjectDependency`, `AgentLearning`, `Ticket`, `Negotiation`, `TicketHistory`

All models are Python dataclasses. UUID primary keys, BIGINT unix timestamps for all date/time fields.

## Installation

Private repository — requires a GitHub personal access token:

```bash
pip install hivemake-models @ git+https://${CR_PAT}@github.com/Really-Bad-Apps/hivemake-models.git
```

## Usage

```python
from hivemake_models import Ticket, TicketStatus, TicketPriority

ticket = Ticket(
    id="...",
    tenant_id="...",
    project_id="...",
    created_by_agent_id="...",
    ticket_type="bug",
    title="NullPointerException",
    description="NPE on line 42",
    status=TicketStatus.OPEN,
    priority=TicketPriority.HIGH,
    created_at=1700000000,
    updated_at=1700000000,
)
```

## Development

```bash
python -m venv .
source bin/activate
pip install -e ".[dev]"
pytest -v
```

Requires Python 3.12+.

## License

Proprietary
