"""Regression: a ticket list cut off by the `gh --limit` is not the whole backlog."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_upstream_updates as upstream  # noqa: E402

BASELINE = {
    "repo": "https://github.com/example/product.git",
    "branch": "main",
    "reviewed_through": "a" * 40,
    "reviewed_date": "2026-10-26",
    "reviewed_pr_through": 100,
}


def _fake_gh(items):
    def runner(args, **kwargs):
        limit = int(args[args.index("--limit") + 1])
        return subprocess.CompletedProcess(
            args, 0, stdout=json.dumps(items[:limit]), stderr=""
        )

    return runner


def test_list_that_hit_the_limit_with_everything_above_the_watermark_is_unavailable(
    monkeypatch,
) -> None:
    # `gh` returns the newest N items. When all N are above the watermark, older
    # unreviewed items were cut off; the 1000 seen must not read as the backlog.
    items = [{"number": 5000 - i, "title": "t"} for i in range(1000)]
    monkeypatch.setattr(upstream.subprocess, "run", _fake_gh(items))
    assert upstream.collect_new_tickets(BASELINE, "pr") is None


def test_list_below_the_limit_is_returned(monkeypatch) -> None:
    items = [{"number": 150, "title": "new"}, {"number": 90, "title": "old"}]
    monkeypatch.setattr(upstream.subprocess, "run", _fake_gh(items))
    assert upstream.collect_new_tickets(BASELINE, "pr") == [items[0]]


def test_full_list_that_reaches_below_the_watermark_is_complete(monkeypatch) -> None:
    items = [{"number": 1100 - i, "title": "t"} for i in range(1000)]  # 1100..101
    items[-1] = {"number": 99, "title": "old"}
    monkeypatch.setattr(upstream.subprocess, "run", _fake_gh(items))
    result = upstream.collect_new_tickets(BASELINE, "pr")
    assert result is not None and len(result) == 999
