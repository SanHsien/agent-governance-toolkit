"""Regression: an <img src> value is a whole path, not a Markdown link with a title."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_links  # noqa: E402


def test_img_src_with_a_space_is_checked_as_one_path(tmp_path: Path) -> None:
    (tmp_path / "my file.png").write_bytes(b"x")
    doc = tmp_path / "doc.md"
    doc.write_text('<img src="my file.png">\n', encoding="utf-8")
    original = check_links.ROOT
    check_links.ROOT = tmp_path.resolve()
    try:
        assert check_links.check_document(doc) == []
    finally:
        check_links.ROOT = original
