"""Scheduling is availability, independent of ticket lifecycle status."""

import time
from typing import TYPE_CHECKING, Optional

from hivemake_models.enums import TicketStatus, WaitingParty, waiting_party

if TYPE_CHECKING:
    from hivemake_models.models import Ticket


def validate_not_before(value: Optional[int]) -> None:
    """UTC Unix seconds, bounded to dates representable by the MCP contract."""
    if value is not None and (type(value) is not int or not 0 <= value <= 253402300799):
        raise ValueError("not_before must be integer Unix seconds between 0 and 253402300799, or null")


def validate_scheduled_offset(value: int) -> None:
    """PostgreSQL OFFSET takes a signed bigint; reject overflow before SQL."""
    if type(value) is not int or not 0 <= value <= 9223372036854775807:
        raise ValueError("scheduled_offset must be an integer between 0 and 9223372036854775807")


def is_scheduled(ticket: "Ticket", now: Optional[int] = None) -> bool:
    now = int(time.time()) if now is None else now
    return (ticket.status in (TicketStatus.OPEN, TicketStatus.ACCEPTED, TicketStatus.IN_PROGRESS) and ticket.not_before is not None
            and ticket.not_before > now)


def ticket_waiting_party(ticket: "Ticket", now: Optional[int] = None) -> WaitingParty:
    return WaitingParty.NOBODY if is_scheduled(ticket, now) else waiting_party(ticket.status)
