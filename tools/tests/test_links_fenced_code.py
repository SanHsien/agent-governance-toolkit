"""Regression: links inside fenced code blocks are examples, not links."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_links  # noqa: E402


def test_links_inside_fenced_code_are_ignored(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "```markdown\n[example](definitely-missing.md)\n```\n"
        "~~~\n[tilde](also-missing.md)\n~~~\n",
        encoding="utf-8",
    )
    assert check_links.check_document(doc) == []


def test_links_outside_the_fence_are_still_checked(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "```\n[a](x.md)\n```\n[real](missing-real.md)\n", encoding="utf-8"
    )
    assert len(check_links.check_document(doc)) == 1
