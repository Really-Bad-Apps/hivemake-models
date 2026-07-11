from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class KnowledgeMatch:
    """One similar-ticket recall hit, returned by
    `find_similar_tickets` on the client SDK / MCP tool.

    `score` is an implementation-defined ranking value, normalized so
    higher = better within a single response batch. It is NOT a raw
    cognee similarity or distance: cognee's CHUNKS REST response drops
    the underlying vector score (`chunks_retriever.py`), so Phase E's
    KnowledgeService derives `score` from the returned batch's ordering
    or an equivalent signal. Do not compare scores across separate
    responses or against absolute thresholds.

    `project` is Optional because hive-level tickets (no project
    association) are legitimate; the recall path preserves that shape.

    Isolation post-condition: `hive_id` will always be in the caller's
    visible-hive set (own + open + owner_scope). Callers can treat it
    as a display-only field, not a permission gate. This is enforced by
    KnowledgeService, not by this dataclass.
    """
    ticket_id: UUID
    hive_id: UUID
    ticket_type: str
    final_status: str
    score: float
    snippet: str
    project: Optional[str] = None
