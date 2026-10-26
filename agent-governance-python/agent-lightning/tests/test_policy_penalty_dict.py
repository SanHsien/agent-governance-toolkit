"""Regression: dict violations are charged by their severity (upstream #4422)."""

from __future__ import annotations

from agent_lightning_gov.reward import policy_penalty


def test_dict_violation_is_charged_by_its_severity() -> None:
    assert policy_penalty([{"severity": "critical"}]) == policy_penalty(
        [type("V", (), {"severity": "critical"})()]
    )
    assert policy_penalty([{"severity": "critical"}, {"severity": "low"}]) == -101.0


def test_dict_without_severity_falls_back_to_medium() -> None:
    assert policy_penalty([{}]) == policy_penalty([{"severity": "medium"}])
