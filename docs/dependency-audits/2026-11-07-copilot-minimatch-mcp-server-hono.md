---
title: "copilot extension minimatch and mcp-server @hono/node-server advisory remediation"
last_reviewed: 2026-11-07
owner: agt-maintainers
---

# 2026-11-07 - minimatch 11.0.1 in the copilot extension; @hono/node-server 2.1.3 in the mcp-server extension

Follow-up to `2026-11-07-minimatch-advisory.md` (which covered mcp-server and `agent-governance-typescript`). Remediates the two remaining Dependabot alerts that the same pass left open, both created 2026-11-07:

- #303: `minimatch` GHSA-g3hv-75wg-m249 in `agent-governance-python/agent-os/extensions/copilot`.
- #304: `@hono/node-server` GHSA-rmxm-3fg6-px4f in `agent-governance-python/agent-os/extensions/mcp-server`.

## Which dependencies changed and why

| Package | From | To | Files |
| --- | --- | --- | --- |
| `minimatch` (root copy, copilot) | 10.2.5 | 11.0.1 | `extensions/copilot/package-lock.json` |
| `minimatch` nested under `glob` 10.5.0 (copilot) | 9.0.9 | removed (deduped to root 11.0.1) | `extensions/copilot/package-lock.json` |
| `@isaacs/nonrecursive-glob-match` (copilot) | (absent) | 1.0.3 (dependency of minimatch 11) | `extensions/copilot/package-lock.json` |
| `@hono/node-server` (mcp-server) | 2.1.1 | 2.1.3 | `extensions/mcp-server/package-lock.json` |

Overrides added to `package.json`:

- `extensions/copilot`: `"minimatch@^10": "11.0.1"`, `"glob@^10": { "minimatch": "11.0.1" }` and `"@isaacs/nonrecursive-glob-match": "1.0.3"`. Same scoped form as `agent-governance-typescript`, for the same reason: `test-exclude` 6.0.0 and its `glob` 7.2.3 (via `babel-plugin-istanbul`, used by `jest --coverage`) call `require('minimatch')` as a function, which minimatch 11 (an object export) breaks with `TypeError: minimatch is not a function`. Their minimatch 3.1.5 copy (with `brace-expansion` 1.1.21, `balanced-match` 1.0.2, `concat-map`) is outside the advisory range (`>= 7.0.0`) and is left untouched.
- `extensions/mcp-server`: `"@hono/node-server": "2.1.3"` (the `minimatch` and `nonrecursive-glob-match` overrides already exist from the earlier pass).

Lockfiles were regenerated with `npm install --package-lock-only --ignore-scripts`. For copilot the stale nested lock entries (`glob/node_modules/{minimatch,brace-expansion,balanced-match}`) had to be dropped first so npm would apply the `glob@^10` override, as in the TypeScript SDK; a first attempt left minimatch un-hoisted, so the intermediate nested 11.0.1 copies were dropped too and the final lock keeps a single root `node_modules/minimatch` 11.0.1. Lock diff scope: copilot 12 insertions and 37 deletions (root minimatch, new nonrecursive-glob-match, removal of the three nested `glob/node_modules` entries); mcp-server 3 insertions and 3 deletions (`@hono/node-server` version, resolved, integrity).

## Security advisory relevance

- GHSA-g3hv-75wg-m249 (CVE-2026-118764, Medium): minimatch pattern amplification; affected `>= 7.0.0, < 11.0.1`; first patched 11.0.1; published 2026-10-30T23:09:55Z. Alert #303 created 2026-11-07T10:28:37Z.
- GHSA-rmxm-3fg6-px4f (CVE-2026-118663, Medium): `@hono/node-server` `serveStatic` double-decodes the request path (affected `>= 1.19.10, < 2.1.3`; first patched 2.1.3; published 2026-10-28T21:05:00Z). Alert #304 created 2026-11-07T10:28:37Z. No patched 1.x exists, so the 2.x line is required (the 2026-11-04 audit reached the same conclusion for the other two packages).

## Provenance and version age

| Package | Version | Published (UTC) | Age on 2026-11-07 | License |
| --- | --- | --- | --- | --- |
| `minimatch` | 11.0.1 | 2026-10-27T22:26:03Z | 11 days | BlueOak-1.0.0 |
| `@isaacs/nonrecursive-glob-match` | 1.0.3 | 2026-10-28T19:50:48Z | 10 days | BlueOak-1.0.0 |
| `@hono/node-server` | 2.1.3 | 2026-09-29T06:10:34Z | 39 days | MIT |

All clear the seven-day cooling-off rule. Newer `@hono/node-server` releases 2.1.4 (2026-10-08) and 2.1.5 (2026-10-13) would also clear it, but 2.1.6 (2026-11-02) does not; the first patched version is chosen, following the 2026-11-04 precedent.

## Breaking change risk assessment

Risk: low.
1. minimatch: the 10.x to 11.x bump changes the CommonJS export from a callable function to an object. In copilot the only function-style callers are `test-exclude` 6.0.0 and its `glob` 7.2.3, which keep minimatch 3.1.5 through the scoped overrides. The 11.0.1 consumers (eslint, `@eslint/config-array`, `@typescript-eslint/typescript-estree`, `glob` 10.5.0) use the named API and are development tools (`dev: true`). minimatch 11 declares `engines.node "18 || 20 || >=22"`, compatible with the package's engines.
2. @hono/node-server: the only consumer is transitive, `@modelcontextprotocol/sdk@1.32.1`, whose manifest declares `"@hono/node-server": "^1.19.9 || ^2.0.5"` (verified with `npm view`), so 2.1.3 is inside its accepted range. The lock already resolved 2.1.1 (a 2.x release), so this is a patch-level change within the line. 2.x declares `engines.node >=20` while `extensions/mcp-server/package.json` declares `>=18.0.0`; this is the same difference accepted for `policy-engine/sdk/node` on 2026-11-04.

## Tests run

- `extensions/copilot`: `npm ci --ignore-scripts` exit 0, `npm run build` exit 0, `npm run lint` exit 0, `npm test` exit 0 (3 suites, 17 tests passed; includes the `typecheck:tests` pretest). Coverage smoke `node node_modules/jest/bin/jest.js --coverage --coverageDirectory <temp>` exit 0 (3 suites, 17 tests), which exercises `test-exclude`. `npm audit` no longer lists minimatch (remaining findings are unrelated jest-runtime and similar).
- `extensions/mcp-server`: `npm ci --ignore-scripts` exit 0, `npm run build` exit 0, `npm run lint` exit 0, `npm test` exit 0 (no test files; vitest runs with `--passWithNoTests`), `npm audit` exit 0 with 0 vulnerabilities.
- `npm ls`: copilot shows minimatch 11.0.1 everywhere except `test-exclude` 6.0.0 and its `glob` 7.2.3 (3.1.5); mcp-server shows `@hono/node-server@2.1.3` under `@modelcontextprotocol/sdk@1.32.1`.
- Regression tests in `tools/tests/test_fork_product_windows.py`: `test_minimatch_advisory_remediation_leaves_no_vulnerable_lock_entry` now covers copilot (no lock entry in `>= 7.0.0, < 11.0.1`, root 11.0.1, pinned nonrecursive-glob-match, `test-exclude` keeps minimatch below 7 in both jest packages) and `test_hono_node_server_advisory_remediation_and_lock_integrity` now covers the mcp-server extension (override present, lock version >= 2.1.3 and equal to the override). Both fail on the previous HEAD for these packages.
- Monorepo gate: `pwsh -NoProfile -File tools/dev_check.ps1`.

## npm version note

`Fork product Windows` runs npm 10.9.9 (Node 22.23.4). The range-keyed overrides used here (same form as the TypeScript SDK originally used) passed `npm ci --ignore-scripts --dry-run` under `npx npm@10.9.9` for both extensions, and the Copilot extension job was green on `main`. The TypeScript SDK needed a different form because of a rimraf/glob 13 edge that npm 10 resolves differently; see `2026-11-07-minimatch-advisory.md`, "CI correction". If the copilot lock is ever regenerated, re-check it with npm 10.9.9 as well.

## Not covered here

Open alerts remaining after this change (unrelated advisories): #300 (`@hono/node-server`, `agent-mesh/packages/mcp-proxy`), #301 (`follow-redirects`, copilot), #292 and #286 (`deepmerge`), #306 to #312 (`pypdf`, caas), #316 (`cedar-policy`).

## Rollback plan

Revert the `package.json` overrides and `package-lock.json` entries in the two extensions to the previous commit.
