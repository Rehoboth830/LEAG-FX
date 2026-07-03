"""Tests for src/common/experiment_tracker.py"""

from src.common.experiment_tracker import EXPERIMENTS_LOG, log_experiment


def test_log_experiment_writes_entry_to_csv():
    entry = log_experiment(
        phase="Phase 1",
        description="Dummy entry to prove experiment tracking works",
        parameters="none",
        result="tracker functioning as expected",
        notes="written automatically by test_experiment_tracker.py",
    )

    assert EXPERIMENTS_LOG.exists()
    log_contents = EXPERIMENTS_LOG.read_text()
    assert entry.description in log_contents
    assert entry.result in log_contents


def test_log_experiment_returns_entry_with_all_fields():
    entry = log_experiment(
        phase="Phase 1",
        description="Second dummy entry",
        parameters="n/a",
        result="ok",
    )

    assert entry.phase == "Phase 1"
    assert entry.description == "Second dummy entry"
    assert entry.result == "ok"
    assert entry.timestamp  # non-empty
