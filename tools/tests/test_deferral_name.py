"""Regression: deferrals match package names under PEP 503 normalization."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_dependency_freshness as freshness  # noqa: E402


def test_deferral_matches_the_normalized_package_name(monkeypatch) -> None:
    # `typing_extensions`, `typing-extensions` and `Typing.Extensions` are one
    # package; a deferral written with one spelling must cover the others.
    monkeypatch.setattr(freshness, "fetch_pypi_version", lambda name, timeout=10.0: "5.0.0")
    rows = [
        {
            "name": "typing_extensions",
            "minimum": "4",
            "requirement": "typing_extensions>=4",
            "source": "requirements-dev.txt",
            "hold": "",
        }
    ]
    status = freshness.collect_status(rows, {"typing-extensions": ("5.0.0", "reviewed")})
    assert status[0]["deferred_reason"] == "reviewed"
    assert not freshness.needs_review(status[0])


def test_load_deferrals_normalizes_keys(tmp_path: Path) -> None:
    path = tmp_path / "d.json"
    path.write_text(
        '{"deferrals": {"Typing_Extensions": {"deferredLatest": "5", "reason": "r"}}}',
        encoding="utf-8",
    )
    assert "typing-extensions" in freshness.load_deferrals(path)
