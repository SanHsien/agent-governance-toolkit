---
title: "minimatch advisory remediation (GHSA-g3hv-75wg-m249)"
last_reviewed: 2026-11-07
owner: agt-maintainers
---

# 2026-11-07 - minimatch -> 11.0.1 in mcp-server extension and TypeScript SDK

Remediates Dependabot alerts #305 (`agent-governance-python/agent-os/extensions/mcp-server`) and #315 (`agent-governance-typescript`), both created 2026-11-07. The two Dependabot security-update jobs for `minimatch` (runs 42364114916 and 42364114656, commit `42e75556`) failed with `update_not_possible`: Dependabot found that the only version path would downgrade `@typescript-eslint/eslint-plugin` from 8.70.1 to 7.0.0, because the installed `eslint` 10.11.0, `@eslint/config-array` 0.23.5 and `@typescript-eslint/typescript-estree` 8.70.1 declare `minimatch` ranges `^10.2.x` that exclude the patched 11.x line. An `overrides` pin resolves this without touching those packages.

## Which dependencies changed and why

| Package | From | To | Files |
| --- | --- | --- | --- |
| `minimatch` (root copy) | 10.2.5 | 11.0.1 | both `package-lock.json` files |
| `minimatch` nested under `glob` 10.5.0 | 9.0.9 | removed (deduped to root 11.0.1) | `agent-governance-typescript/package-lock.json` |
| `@isaacs/nonrecursive-glob-match` | (absent) | 1.0.3 (new dependency of minimatch 11) | both `package-lock.json` files |

Overrides added to `package.json`:

- `agent-governance-python/agent-os/extensions/mcp-server`: `"minimatch": "11.0.1"` and `"@isaacs/nonrecursive-glob-match": "1.0.3"`. This package has no minimatch 3.x consumer, so a global pin is safe.
- `agent-governance-typescript`: global `"minimatch": "11.0.1"` plus an explicit exemption `"test-exclude": { "minimatch": "3.1.5", "glob": { "minimatch": "3.1.5" } }`, and `"@isaacs/nonrecursive-glob-match": "1.0.3"`. This replaced an earlier range-keyed form (`"minimatch@^10": "11.0.1"` and `"glob@^10": { "minimatch": "11.0.1" }`); see "CI correction" below.

Lockfiles were regenerated with `npm install --package-lock-only --ignore-scripts`. Intentionally unchanged: `test-exclude` 6.0.0 keeps its nested `minimatch` 3.1.5 and `glob` 7.2.3 together with their `brace-expansion` 1.1.21, `balanced-match` 1.0.2 and `concat-map`.

## Security advisory relevance

- GHSA-g3hv-75wg-m249 (CVE-2026-118764, Medium): minimatch pattern amplification in `firstPhasePreProcess()` when `optimizationLevel >= 2` leads to excessive CPU and memory use (affected `>= 7.0.0, < 11.0.1`; first patched version 11.0.1; published 2026-10-30T23:09:55Z).
- The 9.0.9 copy nested under `glob` in the TypeScript SDK is inside the affected range too, even though Dependabot reported a single alert for that manifest; the scoped override clears it as well. The 3.1.5 copy under `test-exclude` is outside the range and is deliberately left alone.

No patched release exists on the 7.x-10.x lines, so the 11.x major line is required.

## Provenance and version age

| Package | Version | Published (UTC) | Age on 2026-11-07 | License |
| --- | --- | --- | --- | --- |
| `minimatch` | 11.0.1 | 2026-10-27T22:26:03Z | 11 days | BlueOak-1.0.0 |
| `@isaacs/nonrecursive-glob-match` | 1.0.3 | 2026-10-28T19:50:48Z | 10 days | BlueOak-1.0.0 |

Both clear the seven-day cooling-off rule. Newer minimatch releases 11.0.4 (2026-11-02) and 11.0.5 (2026-11-05) do not, so the first patched version is selected (precedent: `docs/fork/DECISIONS.md` 2026-10-28, 2026-11-04). minimatch 11.0.1 declares `@isaacs/nonrecursive-glob-match ^1.0.1`; the newest 1.1.0 was published 2026-11-05T21:38:25Z (2 days, fails the rule), so it is pinned to 1.0.3 (which satisfies `^1.0.1`) by override.

## Breaking change risk assessment

Risk: low for the consumers that move to 11.x, with one real hazard that the `test-exclude` exemption avoids.
1. minimatch 11 changes the CommonJS export from a callable function (3.x style `require('minimatch')(...)`) to an object. Callers written for 3.x break at runtime with `TypeError: minimatch is not a function`. `test-exclude` 6.0.0 (used by `babel-plugin-istanbul` for `jest --coverage`) and its nested `glob` 7.2.3 do exactly that (`is-outside-dir-win32.js`). A global `"minimatch": "11.0.1"` override in the TypeScript SDK was tried first and broke `jest --coverage`; it was replaced by the `test-exclude` exemption above (first as range-keyed overrides, then corrected, see "CI correction"). The 3.1.5 copies are outside the advisory range (`>= 7.0.0`), so leaving them alone is both safe and necessary.
2. The remaining consumers (eslint, `@eslint/config-array`, `@typescript-eslint/typescript-estree`, `glob` 10.5.0 and `glob` 13.0.6) are development tools that use the named API. Nothing is shipped in a distributable; the packages are `dev: true`.
3. minimatch 11 declares `engines.node "18 || 20 || >=22"`, compatible with both packages' `engines.node ">=18.0.0"` and the Node 22 used by CI.

## Tests run

- `agent-governance-typescript`: `npm ci --ignore-scripts` exit 0, `npm run build` exit 0, `npm run lint` exit 0, `npm test` exit 0 (43 suites, 712 tests passed). Coverage smoke `node node_modules/jest/bin/jest.js --config jest.config.js --coverage --coverageDirectory <temp> tests/audit.test.ts` exit 0 (17 tests passed).
- `agent-governance-python/agent-os/extensions/mcp-server`: `npm ci --ignore-scripts` exit 0, `npm run build` exit 0, `npm run lint` exit 0, `npm test` exit 0 (the package has no test files; vitest runs with `--passWithNoTests`). It has no Fork product Windows job.
- `npm ls minimatch @isaacs/nonrecursive-glob-match`: mcp-server shows only minimatch 11.0.1. The TypeScript SDK shows minimatch 11.0.1 for eslint, `glob` 10.5.0 and `glob` 13.0.6, and minimatch 3.1.5 for `test-exclude` 6.0.0 and its `glob` 7.2.3 (outside the advisory range).
- Regression test: `tools/tests/test_fork_product_windows.py::test_minimatch_advisory_remediation_leaves_no_vulnerable_lock_entry` asserts no lock entry in `>= 7.0.0, < 11.0.1`, root minimatch 11.0.1, nonrecursive-glob-match 1.0.3, and that `test-exclude` keeps a minimatch below 7 (fails on clean HEAD, passes after the fix).
- Monorepo gate: `pwsh -NoProfile -File tools/dev_check.ps1`.

## CI correction (npm version)

The first version of the TypeScript SDK fix used the range-keyed overrides above and was green under the local npm 11.20.0 (Node 26), but `Fork product Windows` / `fork typescript SDK (Windows)` failed on `main` (run 42371378694, earlier 42368203339 and 42367260399): `npm ci --ignore-scripts` under the CI toolchain (Node 22.23.4, npm 10.9.9, per the setup-node log) stopped with `EUSAGE ... Missing: minimatch@10.2.6 from lock file`. Reproduced locally with `npx npm@10.9.9 ci --ignore-scripts`. npm 10.9.9 does not apply the range-keyed overrides to every nested consumer: re-resolving with it left `rimraf` 6.1.3's nested `glob` 13 on minimatch 10.2.6 (inside the vulnerable range), while npm 11 had hoisted everything to 11.0.1, so the committed lock was not what npm 10 computes from the manifest. The copilot extension (same range-keyed form) and mcp-server still passed `npm ci` under npm 10.9.9, but the TypeScript SDK has the extra rimraf/glob 13 edge that triggers it.

Fix: use the global pin with the explicit `test-exclude` exemption. Under both npm 10.9.9 and npm 11.20.0 this resolves to root minimatch 11.0.1 plus `test-exclude/node_modules/minimatch` 3.1.5 and nothing else, so the committed lockfile is unchanged and `npm ci` passes with both. Lesson: the local npm (11.x) is newer than the one bundled with CI's Node 22 (10.9.x); verify lockfile and override changes with `npx npm@10.9.9 ci --ignore-scripts` as well. Do not regenerate lockfiles with npm 10 either: it drops the `libc` fields (18 lines) that npm 11 writes.

## Not covered here

Alert #303 (the same advisory in `agent-governance-python/agent-os/extensions/copilot`) and alert #304 (`@hono/node-server` in the mcp-server extension) are separate and remain open.

## Rollback plan

Revert the `package.json` overrides and `package-lock.json` entries in both packages to the previous commit.
