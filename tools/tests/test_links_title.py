"""Regression: a Markdown link title is not part of the link target."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_links  # noqa: E402


def test_link_with_a_title_resolves_to_its_target() -> None:
    doc = check_links.ROOT / "FORK.md"
    assert check_links._missing_relative(doc, 'NOTICE.md "the notice"') is None
    assert check_links._missing_relative(doc, "NOTICE.md 'the notice'") is None
    assert check_links._missing_relative(doc, '<NOTICE.md> "the notice"') is None
    assert check_links._missing_relative(doc, 'no-such.md "t"') is not None
