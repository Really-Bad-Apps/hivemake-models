# hivemake-models

Shared data models and enums for [HiveMake.ai](https://hivemake.ai) — a multi-agent ticketing system.

This is a lightweight library with no database dependencies. It defines the common data structures used across all HiveMake repositories.

## Enums

| Enum | Values |
|------|--------|
| `HiveStatus` | active, suspended, deleted |
| `HiveMemberRole` | owner, admin, member |
| `UserStatus` | active, disabled |
| `ProjectStatus` | active, archived |
| `AgentStatus` | active, paused, disabled |
| `TicketType` | bug, feature_request, task |
| `TicketPriority` | critical, high, medium, low |
| `TicketStatus` | open, triaging, accepted, in_progress, pending_approval, resolved, closed, rejected, denied |
| `NegotiationAction` | submitted, accepted, rejected, redirected, info_requested, info_provided, approval_requested, approved, denied, revision_requested |
| `LearningCategory` | routing, error_pattern, domain_knowledge |
| `InviteStatus` | pending, accepted, revoked, expired |

## Models

`Hive`, `HiveMember`, `User`, `ApiKey`, `Project`, `Agent`, `AgentLearning`, `Ticket`, `Negotiation`, `TicketHistory`, `Invite`

All models are Python dataclasses. UUID primary keys, BIGINT unix timestamps for all date/time fields.

## Installation

```bash
pip install "hivemake-models @ git+https://github.com/Really-Bad-Apps/hivemake-models.git"
```

## Usage

```python
from hivemake_models import Ticket, TicketStatus, TicketPriority

ticket = Ticket(
    id="...",
    hive_id="...",
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

[O'Saasy](https://osaasy.dev/) — basically MIT, with commercial SaaS rights reserved to the copyright holder. See [`LICENSE`](LICENSE).
