from types import SimpleNamespace

import pytest

from hivemake_models import TicketStatus, WaitingParty, is_scheduled, ticket_waiting_party


@pytest.mark.parametrize('status', list(TicketStatus))
def test_future_availability_only_applies_to_assignee_work(status: TicketStatus) -> None:
    ticket = SimpleNamespace(status=status, not_before=2000)
    deferred = status in (TicketStatus.OPEN, TicketStatus.ACCEPTED, TicketStatus.IN_PROGRESS)
    assert is_scheduled(ticket, 1999) is deferred
    assert not is_scheduled(ticket, 2000)
    if deferred:
        assert ticket_waiting_party(ticket, 1999) == WaitingParty.NOBODY
        assert ticket_waiting_party(ticket, 2000) == WaitingParty.ASSIGNEE
    elif status == TicketStatus.INFO_REQUESTED:
        assert ticket_waiting_party(ticket, 1999) == WaitingParty.CREATOR
    elif status == TicketStatus.ESCALATED:
        assert ticket_waiting_party(ticket, 1999) == WaitingParty.HUMAN
