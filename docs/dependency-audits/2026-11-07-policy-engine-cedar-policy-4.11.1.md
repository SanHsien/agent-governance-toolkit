---
title: "policy-engine cedar-policy advisory remediation (alert #316)"
last_reviewed: 2026-11-07
owner: agt-maintainers
---

# 2026-11-07 - cedar-policy 4.11.0 -> 4.11.1 in policy-engine (and its coding_agent example lock)

Remediates Dependabot alert #316 (`policy-engine/Cargo.lock`, scope: runtime, severity low), created 2026-11-07T10:28:40Z. `cedar-policy` is a transitive dependency: the workspace crate `agent_control_specification_core` forwards its `cedar` feature to the registry crate `agent-control-spec` 0.4.0-alpha.4, whose optional dependency is `cedar-policy ^4`. No `Cargo.toml` names cedar-policy, so only the lockfile moves; follow-upstream does not apply because the version is chosen by the lock, not by a manifest upstream controls.

## Which dependencies changed and why

| Package | From | To | Files |
| --- | --- | --- | --- |
| `cedar-policy` | 4.11.0 | 4.11.1 | `policy-engine/Cargo.lock`, `policy-engine/examples/coding_agent/app/Cargo.lock` |
| `cedar-policy-core` | 4.11.0 | 4.11.1 | same two files |
| `cedar-policy-formatter` | 4.11.0 | 4.11.1 | same two files |

Each lock diff is 6 insertions and 6 deletions: `version` and `checksum` of the three crates. The dependency lists of the three crates are identical between 4.11.0 and 4.11.1 (no new crate, no removed crate). The example lock (`coding_agent/app`) was not flagged by Dependabot but locked the same vulnerable 4.11.0; it is fixed in the same pass so no tracked lock stays in the advisory range. `agent-governance-rust/Cargo.lock` and `benchmarks/prompt-injection/harness/agt-rules-baseline/Cargo.lock` already lock 4.13.0 and are untouched.

### How the lock was edited

`cargo update -p cedar-policy --precise 4.11.1` was tried first. Besides the three cedar crates it rewrote eight unrelated `windows-sys` dependency edges (for example `errno`, `rustix`, `socket2`, `tempfile`, moved from 0.61.2 to 0.52.0 or 0.60.2), which is churn in crates that have nothing to do with the advisory and drops them to older `windows-sys` copies. That output was discarded and the six lines were edited by hand instead, with the checksums taken from that run. Cargo itself verified the result: `cargo metadata --locked` exits 0 in both directories (it would refuse a lock that needed changes, and it checks the downloaded crate checksums), and `cargo test --locked` below builds against it.

## Security advisory relevance

- GHSA-c33x-vcv4-vg3g (Low, published 2026-10-29T16:35:04Z): Cedar JSON template `is in` scope missing slot-id validation allows a link panic and decision divergence. Affected `cedar-policy >= 4.0.0, < 4.11.1` (first patched 4.11.1); also `>= 3.0.0, < 3.4.3` and the `@cedar-policy/cedar-wasm` package, neither of which is used here. Alert #316 is on `policy-engine/Cargo.lock`.
- Relevance: the `cedar` feature is on by default in `agent_control_specification_core` (`default = ["opa", "cedar"]`), so the vulnerable crate is compiled into the policy engine. A panic during template linking is a denial-of-service risk, and the "decision divergence" part is the reason to take the fix even though the severity is Low.

## Provenance and version age

| Package | Version | Published (UTC) | Age on 2026-11-07 | License |
| --- | --- | --- | --- | --- |
| `cedar-policy` | 4.11.1 | 2026-06-09T15:19:25Z | 151 days | Apache-2.0 |
| `cedar-policy-core` | 4.11.1 | 2026-06-09T15:19:21Z | 151 days | Apache-2.0 |
| `cedar-policy-formatter` | 4.11.1 | 2026-06-09T15:19:23Z | 151 days | Apache-2.0 |

Clears the seven-day cooling-off rule by a wide margin, and is the first patched version (the repo's earlier entries pin the first patched release). Newer releases exist: 4.11.2 (2026-06-22), 4.12.0 (2026-07-28), 4.13.0 (2026-09-15, already used by `agent-governance-rust`), 4.14.0 (2026-10-17) all clear the rule, and 4.14.1 (2026-11-02, 5 days) does not. They are not taken because this alert only needs 4.11.1 and a minor jump across the Cedar language/API line is a separate change; the three crates must move together (`cedar-policy` pins its core and formatter exactly) and 4.11.1 keeps the crate graph byte-identical. `cedar-policy` 4.11.1 declares rust-version 1.89; the fork Windows jobs use the stable toolchain and the local build and tests succeeded on the installed toolchain.

## Breaking change risk assessment

Risk: low. Patch release inside the same minor; the lock graph is unchanged apart from the three versions and checksums. Consumers are `agent-control-spec` (range `^4`) and the example app through `agent_control_specification` by path. A newer Cedar minor remains a separate decision if `agent-governance-rust` and `policy-engine` should be aligned.

## Tests run

All with `C:\Windows\System32` first on `PATH`:
- `cargo metadata --locked --format-version 1` in `policy-engine` and in `policy-engine/examples/coding_agent/app`: exit 0.
- `cargo test --locked --no-fail-fast -p agent_control_specification_core -p agent_control_specification` in `policy-engine`: every suite passes except one: `host::tests::from_path_zero_config_evaluates_rego_manifest` (left `Deny`, right `Allow`). That test fails identically on the unmodified lock (run separately against the original `Cargo.lock` with the same command, exit 101, same assertion). It exercises the Rego/OPA path and this machine has no `opa` binary on `PATH`, which is the likely cause but was not confirmed beyond that; it does not involve cedar. Passing: `agent_control_specification` lib 46 of 47, `agent_loop_exercise` 9, `conformance_corpus` 3, `fail_closed_error_parity` 1, `ffi_roundtrip` 10, `streaming_conformance` 5, `upstream_compatibility` 5; `agent_control_specification_core` lib 17, `committed_manifests` 1, `yaml_parser` 12.
- Regression test: `tools/tests/test_fork_product_windows.py::test_cedar_policy_advisory_remediation_leaves_no_vulnerable_cargo_lock` asserts that every tracked `Cargo.lock` locking cedar-policy is at or above 4.11.1 and that the three cedar crates share a version.
- Monorepo gate: `pwsh -NoProfile -File tools/dev_check.ps1`.

## Rollback plan

Revert the two `Cargo.lock` files to the previous commit.
