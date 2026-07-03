"""Tests for src/knowledge_base/query.py"""

from src.knowledge_base.query import (
    get_entries_by_category,
    get_entry,
    get_related_entries,
    load_all_entries,
)


def test_load_all_entries_returns_all_sixteen():
    entries = load_all_entries()
    assert len(entries) == 16


def test_get_entry_returns_correct_entry():
    entry = get_entry("fed_funds_rate")
    assert entry is not None
    assert entry.title == "Federal Funds Rate"
    assert entry.category == "fed_policy"


def test_get_entry_returns_none_for_missing_id():
    entry = get_entry("does_not_exist")
    assert entry is None


def test_get_entries_by_category_filters_correctly():
    us_entries = get_entries_by_category("us_indicator")
    ids = {e.id for e in us_entries}
    assert ids == {"us_cpi", "us_nfp", "us_gdp", "us_pce"}


def test_get_related_entries_follows_relationships():
    related = get_related_entries("fed_funds_rate")
    related_ids = {e.id for e in related}
    assert "fomc" in related_ids
    assert "boj_policy_rate" in related_ids


def test_get_related_entries_handles_missing_entry_gracefully():
    related = get_related_entries("does_not_exist")
    assert related == []


def test_every_entry_has_why_it_matters_field_populated():
    entries = load_all_entries()
    for entry_id, entry in entries.items():
        assert (
            entry.why_it_matters_for_usdjpy.strip() != ""
        ), f"{entry_id} is missing why_it_matters_for_usdjpy content"
