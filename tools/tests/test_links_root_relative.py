"""Regression: GitHub resolves `/path` links against the repository root."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_links  # noqa: E402


def test_root_relative_link_resolves_against_the_repo_root() -> None:
    doc = check_links.ROOT / "docs" / "fork" / "DEVELOPMENT.md"
    assert check_links._missing_relative(doc, "/FORK.md") is None
    assert check_links._missing_relative(doc, "/no-such-file.md") is not None
