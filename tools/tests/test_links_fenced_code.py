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


def test_longer_fence_is_not_closed_by_a_shorter_one() -> None:
    text = "````md\n```\n[x](nope1.md)\n```\n````\n[y](nope2.md)\n"
    assert check_links.strip_fenced_code(text) == "[y](nope2.md)"


def test_indented_four_spaces_is_not_a_fence() -> None:
    text = "    ```\n[z](nope3.md)\n"
    assert "nope3.md" in check_links.strip_fenced_code(text)


def test_closing_fence_must_not_carry_an_info_string() -> None:
    text = "```\n```md\n[x](a.md)\n```\n[y](b.md)\n"
    assert check_links.strip_fenced_code(text) == "[y](b.md)"
