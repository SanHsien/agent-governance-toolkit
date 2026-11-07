---
title: "npm advisories: mcp-proxy hono, copilot follow-redirects, deepmerge deferral"
last_reviewed: 2026-11-07
owner: agt-maintainers
---

# 2026-11-07 - @hono/node-server 2.1.3 in mcp-proxy; follow-redirects 1.16.2 in the copilot extension; deepmerge deferred

Last npm leg of the 2026-11-07 Dependabot pass (see `2026-11-07-minimatch-advisory.md` and `2026-11-07-copilot-minimatch-mcp-server-hono.md` for the first two). Covers alerts #300, #301, #292 and #286, plus the `engines` note left over from the mcp-server hono bump.

| Alert | Package | Manifest | Decision |
| --- | --- | --- | --- |
| #300 | `@hono/node-server` | `agent-governance-python/agent-mesh/packages/mcp-proxy` | Fixed: override `2.1.3` |
| #301 | `follow-redirects` | `agent-governance-python/agent-os/extensions/copilot` | Fixed: lock refresh to `1.16.2` |
| #292, #286 | `deepmerge` | `agent-governance-typescript`, `extensions/copilot` | Deferral from 2026-10-29 re-confirmed 2026-11-07: no patched release exists |

All four are fork-handled rather than upstream-followed, on the same grounds as the 2026-11-04 and earlier 2026-11-07 entries: the manifests already carry fork `overrides`, upstream has not published a fix for these, and Dependabot cannot express the fix (the hono and minimatch paths) or the lock refresh is trivial (follow-redirects).

## Which dependencies changed and why

| Package | From | To | Files |
| --- | --- | --- | --- |
| `@hono/node-server` (mcp-proxy, transitive via `@modelcontextprotocol/sdk` 1.32.0) | 2.1.1 | 2.1.3 | `mcp-proxy/package.json` (override), `mcp-proxy/package-lock.json` |
| `follow-redirects` (copilot, transitive via `axios` 1.20.0) | 1.16.1 | 1.16.2 | `extensions/copilot/package-lock.json` |
| `engines.node` (mcp-proxy, mcp-server) | `>=18.0.0` | `>=20` | both `package.json`, both `package-lock.json` root entries |

- mcp-proxy: `overrides` gains `"@hono/node-server": "2.1.3"`. The SDK declares `"@hono/node-server": "^1.19.9 || ^2.0.5"` (verified in the lock), so 2.1.3 is inside the accepted range, and the lock already resolved the 2.x line (2.1.1). Lock regenerated with `npm install --package-lock-only --ignore-scripts`; diff scope is 4 insertions and 4 deletions (the `@hono/node-server` version, resolved URL and integrity, plus the root `engines` mirror).
- copilot: no `package.json` change. `axios` 1.20.0 asks for `follow-redirects ^1.16.0`, so `npm update follow-redirects --package-lock-only --ignore-scripts` moves only the one lock entry (3 insertions and 3 deletions). No override is needed because the range already admits the patched version.
- deepmerge: nothing changed (see below).

### engines decision: raise to `>=20` for mcp-server and mcp-proxy

`@hono/node-server` 2.x declares `engines.node >=20`, and it is a runtime dependency of both packages through the MCP SDK (`dependencies`, not dev). The SDK's own range offers a 1.x escape (`^1.19.9`), but no patched 1.x exists (GHSA-rmxm-3fg6-px4f affects `>= 1.19.10, < 2.1.3`), so the override forces 2.x on every install. Keeping `>=18.0.0` would then advertise a Node version the package cannot run on (npm only prints EBADENGINE and installs anyway), which is a silent runtime failure for a Node 18 user. Raising is the honest choice and costs nothing real: Node 18 has been end-of-life since 2025-04, every CI job that builds these packages uses Node 20 or 22 (`.github/workflows/ci.yml`, `fork-product-windows.yml`), and the 2.x line was already what the lockfiles resolved. Applied to the two MCP server packages that now carry the hono override; the `engines` mirror in each `package-lock.json` root entry was regenerated to match.

Not changed here: `policy-engine/sdk/node` still declares `>=18`; the 2026-11-04 decision accepted that difference and it is a napi native binding whose platform packages are published separately, so it needs its own decision (see DECISIONS 2026-11-07). `mastra-agentmesh` declares no `engines`.

## Security advisory relevance

- #300 GHSA-rmxm-3fg6-px4f (CVE-2026-118663, Medium): `@hono/node-server` `serveStatic` double-decodes the request path (affected `>= 1.19.10, < 2.1.3`; first patched 2.1.3; published 2026-10-28T21:05:00Z). Alert created 2026-11-07T10:28:36Z. Scope: runtime.
- #301 GHSA-mrwp-f3q8-3g9p (CVE-2026-116689, High): follow-redirects cross-realm `sensitiveHeaders` arrays are discarded so custom credentials can follow redirects (affected `>= 1.16.0, <= 1.16.1`; first patched 1.16.2; published 2026-10-30T22:59:33Z). Alert created 2026-11-07T10:28:36Z. Scope: runtime (axios in the copilot extension).
- #292 and #286 GHSA-gcqx-w48m-w2h4 (CVE-2026-93753, Low, CVSS 5.3, CWE-1321): `deepmerge` `mergeObject()` allows prototype poisoning of returned objects (affected `>= 4.2.0, <= 4.3.1`; **no first patched version**; published 2026-09-18T18:31:44Z). Alerts created 2026-10-28. Scope: development.

## Provenance and version age

| Package | Version | Published (UTC) | Age on 2026-11-07 | License |
| --- | --- | --- | --- | --- |
| `@hono/node-server` | 2.1.3 | 2026-09-29T06:10:34Z | 39 days | MIT |
| `follow-redirects` | 1.16.2 | 2026-10-25T21:32:25Z | 13 days | MIT |

Both clear the seven-day cooling-off rule. `@hono/node-server` 2.1.6 (2026-11-02) does not, so the first patched version is chosen as in the earlier entries. 1.16.2 is the newest follow-redirects release. No new transitive package is introduced by either bump (the lock diffs touch only the one entry each; `follow-redirects` 1.16.2 has no dependencies and `engines.node >=4.0`).

## Deferral: deepmerge (#292, #286)

**Deferred since 2026-10-29, re-confirmed on 2026-11-07.** The original deferral and its evidence are in `docs/fork/DECISIONS.md` (2026-10-28 and 2026-10-29 deepmerge sections) and the ROADMAP "刻意不做" row; this pass re-checked the facts with current data:

- The advisory lists no first patched version, and npm's `deepmerge` has no release above 4.3.1 (published 2023-03-16T22:58:56Z). The upstream repository's newest tag is `v4.3.1`; its default branch has a single later merge (PR #270, 2026-09-24) and the advisory references upstream issue #273, which this audit did not find resolved by any release.
- `npm ls deepmerge` in both packages shows one path only: `jest` 30.4.2 -> `@jest/core` -> `jest-config` 30.4.2 -> `deepmerge` 4.3.1 (`"deepmerge": "^4.3.1"`), and both lock entries are `dev: true`. It is a test-runner dependency; neither package ships it. The advisory needs an attacker-controlled source object passed to `mergeObject()`, and `jest-config` merges configuration objects built from the repository's own files.
- Replacing it by an `overrides` alias to a different package (for example a `deepmerge`-compatible fork) would trade a Low, dev-only finding for an unvetted package inside the test runner and fails the seven-day provenance review; not done.

Reopen when any one of these holds: the advisory gains a first patched version; `npm view deepmerge version` reports a release above 4.3.1 that is at least seven days old; or `jest-config` drops or replaces the dependency (check `npm ls deepmerge` after a jest bump). Then bump or override to the first patched version, scoped narrowly to the `jest-config` consumer (its ranges are `^4.3.1`), and delete the deferral rows. The regression test `test_deepmerge_unpatched_advisory_is_only_tolerated_with_a_dated_deferral` fails if the dev-only property or this deferral text disappears while a vulnerable lock entry remains. The Dependabot alerts stay open on purpose; no dismissal was made.

## Breaking change risk assessment

Risk: low.
1. hono 2.1.1 to 2.1.3 is a patch release inside the line the lock already resolved; the only change that matters is the `serveStatic` path-decoding fix. Neither package's `src` references `@hono/node-server` or `serveStatic`: mcp-server uses the SDK's stdio transport, and mcp-proxy's `src` has no MCP SDK import at all, so the exposure is the transitive install only. An import smoke run from each package directory against the installed tree (`createRequire` on the package, then `import()` of `@hono/node-server`) printed `transport function hono 2.1.3 function function`: the SDK's `StreamableHTTPServerTransport` still loads and `getRequestListener` and `serve` are exported.
2. follow-redirects 1.16.1 to 1.16.2 is a patch release inside axios's declared range. The fix keeps credentials from following cross-realm redirects, which can only reject a request that previously leaked a header.
3. The `engines` raise is stricter than before only for Node 18 and below, which no CI job uses and which is past end-of-life. Consumers on Node 18 get an EBADENGINE warning (or an error under `engine-strict`) that now matches reality.
4. Scoping: the hono override is a plain pin because the SDK is the only consumer in each package and its range admits 2.1.3. There is no CommonJS-function hazard of the minimatch kind: nothing in either package's `src` imports `@hono/node-server` directly, and the only consumer is the SDK, which accepts the 2.x line by its declared range. The follow-redirects bump needs no override. The `test-exclude` and minimatch 3.x protections from the earlier entries are untouched (no `package.json` override changed in copilot).

## Tests run

- `agent-governance-python/agent-mesh/packages/mcp-proxy`: `npm ci --ignore-scripts` exit 0, `npm run build` exit 0, `npm test` exit 0 (1 file, 11 tests), `npm audit` exit 0 (0 vulnerabilities), `npm ls @hono/node-server` shows 2.1.3 overridden under the SDK. `npm run lint` exits 2 with "No files matching the pattern src" with a file-pattern error: the script is `eslint src` and ESLint 8 without `--ext .ts` matches no TypeScript files. A `package.json` override and engines change cannot cause that, so it is treated as pre-existing and not addressed here (recorded as an open item in DECISIONS).
- `agent-governance-python/agent-os/extensions/copilot`: `npm ci --ignore-scripts` exit 0, `npm run build` exit 0, `npm run lint` exit 0, `npm test` exit 0 (3 suites, 17 tests), coverage smoke `node node_modules/jest/bin/jest.js --coverage --coverageDirectory <temp>` exit 0 (3 suites, 17 tests), `npm ls follow-redirects` shows 1.16.2 under axios 1.20.0. `npm audit` no longer lists follow-redirects; it still lists deepmerge (deferred) and unrelated jest-runtime findings.
- `agent-governance-python/agent-os/extensions/mcp-server`: `npm ci --ignore-scripts` exit 0 with the new `engines`, `npm run build` exit 0, `npm run lint` exit 0, `npm test` exit 0 (no test files), `npm audit` 0 vulnerabilities.
- Regression tests in `tools/tests/test_fork_product_windows.py`: `test_hono_node_server_advisory_remediation_and_lock_integrity` now also covers mcp-proxy and asserts the declared `engines.node` of mcp-server and mcp-proxy is not below the locked hono requirement and matches the lock root entry; `test_follow_redirects_advisory_remediation_leaves_no_vulnerable_lock_entry`; `test_deepmerge_unpatched_advisory_is_only_tolerated_with_a_dated_deferral`.
- Monorepo gate: `pwsh -NoProfile -File tools/dev_check.ps1`.

## Rollback plan

Revert the `package.json` override and `engines` change and the `package-lock.json` entries in mcp-proxy and mcp-server, and the single `follow-redirects` entry in the copilot lock, to the previous commit.
