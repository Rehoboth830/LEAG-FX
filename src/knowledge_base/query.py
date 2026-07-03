"""
Knowledge base query module for LEAG FX.

Loads structured YAML entries from src/knowledge_base/entries/ and makes
them retrievable by code — satisfying FR-2.3 (queryable by a Python
function, not just human-readable). This is what Phase 9 agents will
eventually call to pull domain knowledge into their reasoning.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from src.common.logger import get_logger

logger = get_logger(__name__)

ENTRIES_DIR = Path(__file__).resolve().parent / "entries"


@dataclass
class KnowledgeEntry:
    """A single knowledge base entry, matching the schema in SCHEMA.md."""

    id: str
    title: str
    category: str
    summary: str
    details: str
    why_it_matters_for_usdjpy: str
    related_entries: list
    sources: list
    last_updated: str


def _load_entry_file(file_path: Path) -> KnowledgeEntry:
    """Loads and parses a single YAML entry file into a KnowledgeEntry."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return KnowledgeEntry(**data)


def load_all_entries() -> dict[str, KnowledgeEntry]:
    """
    Loads every entry in the knowledge base.

    Returns:
        A dict mapping entry id -> KnowledgeEntry.
    """
    entries = {}
    for file_path in sorted(ENTRIES_DIR.glob("*.yaml")):
        try:
            entry = _load_entry_file(file_path)
            entries[entry.id] = entry
        except Exception as e:
            logger.error(f"Failed to load knowledge base entry {file_path.name}: {e}")
    logger.info(f"Loaded {len(entries)} knowledge base entries")
    return entries


def get_entry(entry_id: str) -> Optional[KnowledgeEntry]:
    """
    Retrieves a single knowledge base entry by id.

    Args:
        entry_id: the entry's id, e.g. "fed_funds_rate".

    Returns:
        The matching KnowledgeEntry, or None if not found.
    """
    file_path = ENTRIES_DIR / f"{entry_id}.yaml"
    if not file_path.exists():
        logger.warning(f"Knowledge base entry not found: {entry_id}")
        return None
    return _load_entry_file(file_path)


def get_entries_by_category(category: str) -> list[KnowledgeEntry]:
    """
    Retrieves all entries belonging to a given category.

    Args:
        category: one of fed_policy, boj_policy, us_indicator,
                  japan_indicator, market_structure.

    Returns:
        A list of matching KnowledgeEntry objects.
    """
    all_entries = load_all_entries()
    return [e for e in all_entries.values() if e.category == category]


def get_related_entries(entry_id: str) -> list[KnowledgeEntry]:
    """
    Retrieves all entries related to a given entry, following its
    related_entries field.

    Args:
        entry_id: the entry's id to find relations for.

    Returns:
        A list of related KnowledgeEntry objects. Empty if the entry
        doesn't exist or has no related entries.
    """
    entry = get_entry(entry_id)
    if entry is None:
        return []

    related = []
    for related_id in entry.related_entries:
        related_entry = get_entry(related_id)
        if related_entry is not None:
            related.append(related_entry)
        else:
            logger.warning(
                f"Entry '{entry_id}' references missing related entry '{related_id}'"
            )
    return related
