---
title: "@hono/node-server 1.19.17 -> 2.1.3 advisory remediation"
last_reviewed: 2026-11-04
owner: agt-maintainers
---

# 2026-11-04 - @hono/node-server 1.19.17 -> 2.1.3 in mastra-agentmesh and policy-engine Node SDK

Remediates Dependabot alerts #298 and #299; supersedes Dependabot PR #57 (whose lockfile omitted the peerDependencies of `hono-openapi` 1.3.0 (a dependency of `@mastra/core`), causing PR CI run 41891134325 to fail with `npm error code EUSAGE`). The `main` branch Fork product Windows workflow (commit `938ccb42`) is green.

## Which dependencies changed and why

| Package | From | To | Files |
| --- | --- | --- | --- |
| `@hono/node-server` | 1.19.17 | 2.1.3 | `agent-governance-python/agentmesh-integrations/mastra-agentmesh/package-lock.json`, `policy-engine/sdk/node/package-lock.json` |

`package.json` in both packages gains an exact override:
`"@hono/node-server": "2.1.3"`.
Lockfiles are regenerated with `npm install --package-lock-only --ignore-scripts`, updating
only the transitive `@hono/node-server` entry while preserving all required peerDependencies.

## Security advisory relevance

- GHSA-rmxm-3fg6-px4f (CVE-2026-118663, Medium): `@hono/node-server` `serveStatic` decodes the request path a second time, leading to bypass of middleware on static paths (affected `>= 1.19.10, < 2.1.3`; first patched version: 2.1.3; published 2026-10-28T21:05:00Z; Dependabot alerts #298 and #299 created 2026-11-04).

No patched 1.x release exists for this advisory (1.19.18 still falls within the vulnerable range `>= 1.19.10, < 2.1.3`), requiring the 2.x major line.

## Provenance and version age

`@hono/node-server` 2.1.3 was published to npm on 2026-09-29T06:10:34Z under the MIT license. It is older than seven days (36 days old as of 2026-11-04), satisfying the repository cooling-off rule. Version 2.1.6 was released 2026-11-02, which does not clear the seven-day cooling-off window; following the precedent in `docs/fork/DECISIONS.md` (2026-10-28), the first patched version (2.1.3) is selected.

## Breaking change risk assessment

Risk: low. Moving from 1.x to 2.x is a major bump:
1. The only consumer is transitive: `@modelcontextprotocol/sdk@1.32.1`, whose manifest declares `"@hono/node-server": "^1.19.9 || ^2.0.5"`, explicitly accepting the 2.x range.
2. The package is development-scoped in both projects (and optional in `policy-engine/sdk/node`); it is not packaged into public distributables.
3. Node engine requirement: 2.x specifies `engines: node >=20`. While `policy-engine/sdk/node/package.json` declares `engines.node ">=18"`, this difference only triggers an npm engine notice in development and does not affect runtime consumers. CI builds and tests under Node 22.

## Tests run

- `mastra-agentmesh`: `npm ci --ignore-scripts` exit 0, `npm run patch:dependencies && node scripts/patch-provider-utils.mjs --check` exit 0, `npm run build` exit 0, `npm run lint` exit 0, `npm test` (vitest 4 files, 31 passed).
- `policy-engine/sdk/node`: `npm ci --ignore-scripts` exit 0.
- Regression test: `tools/tests/test_fork_product_windows.py::test_hono_node_server_advisory_remediation_and_lock_integrity` (red on clean HEAD, green with 2.1.3 overrides and intact peerDependencies).
- Monorepo gate: `pwsh -NoProfile -File tools/dev_check.ps1` exit 0.

## Rollback plan

Revert `package.json` overrides and `package-lock.json` entries in both packages to the previous commit.
