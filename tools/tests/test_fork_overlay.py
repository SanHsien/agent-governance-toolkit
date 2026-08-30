from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_links  # noqa: E402
import check_upstream_updates as checker  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL_REPO = "microsoft/agent-governance-toolkit"
UNGATED_WORKFLOWS = {
    "fork-maintenance.yml",
    "upstream-check.yml",
    "dependency-freshness.yml",
}


def test_baseline_file_is_valid_and_complete() -> None:
    baseline = checker.load_baseline()

    assert baseline["repo"] == "https://github.com/microsoft/agent-governance-toolkit.git"
    assert baseline["branch"] == "main"
    assert len(baseline["reviewed_through"]) == 40
    assert baseline["reviewed_through"] == "46463ef8689433817fcc0c582a7881f515d4df15"
    # Pinned as a shape, not as a literal. A hardcoded date turns every
    # legitimate upstream review into a test failure, and the pressure is then
    # to edit the test rather than to record the review.
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", baseline["reviewed_date"])
    # Zero is a legitimate watermark -- it means the axis was queried and was
    # empty -- so presence and type are what get pinned.
    assert isinstance(baseline["reviewed_pr_through"], int)
    assert isinstance(baseline["reviewed_issue_through"], int)


def test_workflow_is_scheduled_and_fails_on_unreviewed_commits() -> None:
    workflow = (ROOT / ".github" / "workflows" / "upstream-check.yml").read_text(
        encoding="utf-8"
    )

    assert "schedule:" in workflow
    assert "cron:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tools/check_upstream_updates.py" in workflow
    assert "fetch-depth: 0" in workflow
    assert "exit 1" in workflow


def test_render_markdown_reports_no_new_commits() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-28",
    }

    report = checker.render_markdown(baseline, [])

    assert "No new upstream commits" in report
    assert "docs/fork/DECISIONS.md" in checker.render_markdown(
        baseline,
        [
            {
                "sha": "b" * 40,
                "short": "bbbbbbb",
                "date": "2026-08-28",
                "subject": "example",
                "files": ["README.md"],
            }
        ],
    )


def test_render_markdown_surfaces_check_failure() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-28",
    }

    report = checker.render_markdown(baseline, [], error="git fetch failed")

    assert "Check failed" in report
    assert "git fetch failed" in report


def test_load_baseline_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(checker.UpstreamCheckError):
        checker.load_baseline(tmp_path / "nope.json")


def test_baseline_matches_decisions_record() -> None:
    decisions = (ROOT / "docs" / "fork" / "DECISIONS.md").read_text(encoding="utf-8")
    upstream = (ROOT / "docs" / "fork" / "UPSTREAM.md").read_text(encoding="utf-8")
    baseline = json.loads(
        (ROOT / "tools" / "upstream_baseline.json").read_text(encoding="utf-8")
    )

    assert baseline["reviewed_date"] in decisions
    assert baseline["reviewed_through"][:7] in upstream
    assert "microsoft/agent-governance-toolkit" in decisions


def test_overlay_markdown_links_resolve() -> None:
    failures = 0
    for path in check_links.iter_documents():
        problems = check_links.check_document(path)
        failures += len(problems)
        for problem in problems:
            print(f"{path}: {problem}")
    assert failures == 0


def test_readme_keeps_upstream_english_product_contract() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert not (ROOT / "README.en.md").exists()
    assert "SanHsien 維護型 fork" in readme
    assert "SanHsien/agent-governance-toolkit" in readme
    assert "microsoft/agent-governance-toolkit" in readme
    assert "FORK.md" in readme
    assert "REVIEW.md" in readme
    assert "pip install" in readme
    assert "agent-governance-toolkit" in readme
    assert "Ship agents to production" in readme


def test_link_checker_skips_product_readme_and_scans_review() -> None:
    rels = {path.relative_to(ROOT).as_posix() for path in check_links.iter_documents()}

    assert "README.md" not in rels
    assert "AGENTS.md" not in rels
    assert "REVIEW.md" in rels
    assert "FORK.md" in rels
    assert "NOTICE.md" in rels
    assert "SECURITY.md" in rels
    assert "CONTRIBUTING.md" in rels
    assert "docs/fork/DECISIONS.md" in rels


def test_missing_relative_rejects_path_escape() -> None:
    problem = check_links._missing_relative(ROOT / "FORK.md", "../outside-the-repo")

    assert problem is not None
    assert "逃出 repo 根目錄" in problem
    assert check_links._missing_relative(ROOT / "FORK.md", "NOTICE.md") is None


def test_review_is_windows_first_record() -> None:
    review = (ROOT / "REVIEW.md").read_text(encoding="utf-8")

    assert "Windows-first" in review
    assert "46463ef" in review
    assert "R-01" in review
    assert "R-06" in review
    assert "127.0.0.1" in review
    assert "不回貢" in review
    assert "microsoft/agent-governance-toolkit" in review


def test_agents_overlay_points_at_fork_rules() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")

    assert "SanHsien 維護型 fork overlay" in agents
    assert "FORK.md" in agents
    assert "不要推 `upstream`" in agents
    assert "FORK.md" in claude
    assert "Agent Governance Toolkit" in agents


def test_required_overlay_files_exist() -> None:
    required = (
        "README.md",
        "FORK.md",
        "NOTICE.md",
        "AGENTS.md",
        "CLAUDE.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "REVIEW.md",
        "LICENSE",
        "NOTICE",
        "docs/fork/DEVELOPMENT.md",
        "docs/fork/DECISIONS.md",
        "docs/fork/UPSTREAM.md",
        "docs/fork/CHANGELOG.md",
        "tools/dev_check.ps1",
        "tools/bootstrap_dev.ps1",
        ".cursor/rules/no-upstream-pr.mdc",
        ".ai-quality-gates.json",
    )
    missing = [name for name in required if not (ROOT / name).is_file()]
    assert missing == []


def test_dangerous_workflows_are_gated_to_upstream() -> None:
    official_guard = f"github.repository == '{OFFICIAL_REPO}'"
    workflows = ROOT / ".github" / "workflows"
    gated = [
        path
        for path in workflows.glob("*.yml")
        if path.name not in UNGATED_WORKFLOWS
    ]
    assert gated, "expected upstream workflows to gate"
    for path in gated:
        text = path.read_text(encoding="utf-8")
        assert official_guard in text, path.name


def test_ungated_workflows_are_not_official_repo_only() -> None:
    official_guard = f"github.repository == '{OFFICIAL_REPO}'"
    workflows = ROOT / ".github" / "workflows"
    for name in UNGATED_WORKFLOWS:
        text = (workflows / name).read_text(encoding="utf-8")
        assert official_guard not in text, name


def test_every_workflow_is_classified_gated_or_ungated() -> None:
    names = {path.name for path in (ROOT / ".github" / "workflows").glob("*.yml")}
    gated = {path.name for path in (ROOT / ".github" / "workflows").glob("*.yml")} - UNGATED_WORKFLOWS
    assert names == gated | UNGATED_WORKFLOWS


def test_auto_merge_is_gated() -> None:
    text = (ROOT / ".github" / "workflows" / "auto-merge-dependabot.yml").read_text(
        encoding="utf-8"
    )
    assert f"github.repository == '{OFFICIAL_REPO}'" in text
    assert "dependabot[bot]" in text


def test_fork_workflows_use_python_314() -> None:
    for name in ("fork-maintenance.yml", "upstream-check.yml", "dependency-freshness.yml"):
        text = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        assert 'python-version: "3.14"' in text, name


def test_security_and_contributing_name_the_fork() -> None:
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "SanHsien/agent-governance-toolkit" in security
    assert "SanHsien/agent-governance-toolkit" in contributing
    assert "FORK.md" in security
    assert "FORK.md" in contributing
    assert "aka.ms/SECURITY.md" in security
    assert "microsoft/agent-governance-toolkit" in contributing
    assert "127.0.0.1:8501" in security
    assert "127.0.0.1:8081" in security
    assert "127.0.0.1:8501" in contributing


def test_compose_overlay_binds_loopback() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    openclaw = (
        ROOT / "examples" / "demos" / "openclaw-governed" / "docker-compose.yaml"
    ).read_text(encoding="utf-8")

    assert "127.0.0.1:8501:8501" in compose
    assert '"8501:8501"' not in compose
    assert "--server.address=0.0.0.0" in compose
    assert "127.0.0.1:8081:8081" in openclaw
    assert '"8081:8081"' not in openclaw
    assert "HOST=0.0.0.0" in openclaw


def test_gitignore_covers_fork_reports() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".venv/" in text
    assert ".env" in text
    assert "upstream-review-report.md" in text
    assert "dependency-freshness-report.md" in text
    assert ".agt/" in text


def test_quality_gate_points_at_windows_check() -> None:
    payload = json.loads((ROOT / ".ai-quality-gates.json").read_text(encoding="utf-8"))
    assert payload["enabled"] is True
    assert "tools/dev_check.ps1" in payload["quick"]
