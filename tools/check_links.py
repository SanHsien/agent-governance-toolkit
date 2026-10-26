#!/usr/bin/env python3
"""檢查本 fork overlay 文件之間的相對連結。

只驗 FORK.md、NOTICE.md、REVIEW.md、SECURITY.md、CONTRIBUTING.md
與 docs/fork/。不掃根目錄 README.md／AGENTS.md：那是上游產品契約，頂部 overlay
以外的連結由上游負責。

    python tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_PATTERN = re.compile(r"""(?is)<img[^>]+src=["']([^"']+)["']""")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")
SKIP_NAMES = {
    "upstream-review-report.md",
    "dependency-freshness-report.md",
}

FORK_DOCUMENTS = [
    ROOT / "FORK.md",
    ROOT / "NOTICE.md",
    ROOT / "REVIEW.md",
    ROOT / "SECURITY.md",
    ROOT / "CONTRIBUTING.md",
]


def iter_documents() -> list[Path]:
    documents = [path for path in FORK_DOCUMENTS if path.is_file()]
    fork_docs = ROOT / "docs" / "fork"
    if fork_docs.is_dir():
        documents.extend(sorted(fork_docs.glob("*.md")))
    return [path for path in documents if path.name not in SKIP_NAMES]


def _link_target(raw: str) -> str:
    """The path of a Markdown link target, without its optional title."""
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    parts = raw.split()
    return parts[0] if parts else ""


def _missing_relative(path: Path, target: str, *, markdown: bool = True) -> str | None:
    target = _link_target(target) if markdown else target.strip()
    if not target or target.startswith(SKIP_PREFIXES):
        return None
    file_part = unquote(target.split("#", 1)[0])
    if not file_part:
        return None
    # GitHub renders a leading "/" against the repository root, not the drive root.
    base = ROOT if file_part.startswith("/") else path.parent
    resolved = (base / file_part.lstrip("/")).resolve()
    if not resolved.is_relative_to(ROOT):
        return f"{target} → 逃出 repo 根目錄"
    if resolved.exists():
        return None
    try:
        shown = resolved.relative_to(ROOT)
    except ValueError:
        shown = resolved
    return f"{target} → 找不到 {shown}"


FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def strip_fenced_code(text: str) -> str:
    """Drop fenced code blocks: links shown there are examples, not links.

    Follows CommonMark: a fence is 3+ backticks or tildes indented at most 3
    spaces; it closes on the same character, at least as long, with no info
    string. A backtick fence's info string cannot contain a backtick.
    """
    kept: list[str] = []
    fence = ""
    for line in text.splitlines():
        if fence:
            stripped = line.strip()
            if (
                len(line) - len(line.lstrip(" ")) <= 3
                and stripped
                and set(stripped) == {fence[0]}
                and len(stripped) >= len(fence)
            ):
                fence = ""
            continue
        match = FENCE_OPEN.match(line)
        if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
            fence = match.group(1)
            continue
        kept.append(line)
    return "\n".join(kept)


def check_document(path: Path) -> list[str]:
    problems: list[str] = []
    text = strip_fenced_code(path.read_text(encoding="utf-8"))
    for pattern in (LINK_PATTERN, IMAGE_PATTERN, HTML_SRC_PATTERN):
        for match in pattern.finditer(text):
            missing = _missing_relative(
                path, match.group(1), markdown=pattern is not HTML_SRC_PATTERN
            )
            if missing:
                problems.append(missing)
    return problems


def main() -> int:
    documents = iter_documents()
    if not documents:
        print("找不到任何 fork overlay Markdown 檔")
        return 1

    failures = 0
    for path in documents:
        problems = check_document(path)
        rel = path.relative_to(ROOT)
        if problems:
            failures += 1
            for problem in problems:
                print(f"FAIL {rel}: {problem}")
        else:
            print(f"OK   {rel}")

    print(f"\n共 {len(documents)} 份 overlay 文件，{failures} 份有缺檔。")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
