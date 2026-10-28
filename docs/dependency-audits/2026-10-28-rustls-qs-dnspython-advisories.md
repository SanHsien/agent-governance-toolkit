---
title: rustls 0.23.46, qs 6.16.1 and dnspython 2.9.0 advisory updates
last_reviewed: 2026-10-28
owner: agt-maintainers
---

# rustls 0.23.46, qs 6.16.1 and dnspython 2.9.0 advisory updates

## Which dependencies changed and why

| Package | From | To | Files |
| --- | --- | --- | --- |
| `rustls` | 0.23.45 | 0.23.46 | `agent-governance-rust/Cargo.lock`, `policy-engine/Cargo.lock` |
| `qs` | 6.16.0 / 6.15.2 | 6.16.1 | `package-lock.json` of the Copilot extension, `agent-mesh/services/api`, `mastra-agentmesh` and `policy-engine/sdk/node` |
| `side-channel` (qs 6.16.1 dependency chain) | 1.1.0 | 1.1.1 | `policy-engine/sdk/node/package-lock.json` |
| `dnspython` | 2.8.0 | 2.9.0 | `agent-governance-python/agent-hypervisor/uv.lock` |

The `qs` override in the Copilot extension and `services/api` `package.json`
moves from `6.16.0` to `6.16.1`. `mastra-agentmesh` and `policy-engine/sdk/node`
gain the same exact `qs` override so the lock resolves to the first patched
version instead of the newest (6.17.0 was published 2026-10-27, inside the
seven-day cooling-off window). Only the `Cargo.lock` version and checksum lines
change for rustls. The `dnspython` block in `uv.lock` was replaced in place
(version, sdist and wheel URL and sha256 match PyPI); the rest of the lock is
untouched.

## Provenance and version age

`rustls` 0.23.46 was published to crates.io on 2026-10-14, `qs` 6.16.1 on
2026-10-14 and `dnspython` 2.9.0 on 2026-10-09; all are older than seven days.
Checksums are the registry values recorded in each lockfile.

## Security advisory relevance

- `rustls`: GHSA-h2v8-394m-p7vv, GHSA-c8m5-c952-6cm4, GHSA-w44r-93j7-qv28,
  GHSA-vp88-798v-h67f (all fixed in 0.23.46).
- `qs`: GHSA-6pq8-jhm2-2vcw (fixed in 6.16.1).
- `dnspython`: GHSA-45c3-73f7-pv4m (fixed in 2.9.0).
- `deepmerge` GHSA-gcqx-w48m-w2h4 has no patched release and is deferred; see
  `docs/fork/DECISIONS.md` (2026-10-28).

## Breaking-change risk assessment

Patch releases of the same minor line for `rustls` and `qs`; `dnspython`
2.9.0 requires Python 3.11 or newer, which matches the package's
`requires-python`. `cargo test`, `npm test` and `pytest` results before and
after are identical; see the decision entry for commands and counts.
