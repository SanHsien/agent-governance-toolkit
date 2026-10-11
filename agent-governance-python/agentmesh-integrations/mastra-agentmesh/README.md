# @agentmesh/mastra

Governance, trust verification, and audit middleware for [Mastra](https://mastra.ai) AI agents.

[![npm](https://img.shields.io/npm/v/@agentmesh/mastra)](https://www.npmjs.com/package/@agentmesh/mastra)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

`@agentmesh/mastra` adds three security layers to Mastra tool execution:

| Layer | What It Does |
|-------|-------------|
| **Governance** | Rate limits, content filtering, PII redaction, tool allow/deny lists |
| **Trust** | Agent trust score verification (0-1000 scale) before tool execution |
| **Audit** | Tamper-evident SHA-256 hash chain logging of all tool invocations |

## Install

```bash
npm install @agentmesh/mastra
```

Peer dependencies: `@mastra/core >= 0.10.0`, `zod >= 3.22.0`

## Quick Start

### Wrap any Mastra tool with governance

```typescript
import { createTool } from "@mastra/core";
import { createGovernedTool } from "@agentmesh/mastra";
import { AgentControl } from "agent-control-specification";
import { z } from "zod";

const searchTool = createTool({
  id: "web-search",
  description: "Search the web",
  inputSchema: z.object({ query: z.string() }),
  outputSchema: z.object({ results: z.array(z.string()) }),
  execute: async ({ query }) => ({ results: ["result1"] }),
});

const control = AgentControl.fromPath("./manifest.yaml");

// Add ACS policy enforcement + trust + audit in one call
const governedSearch = createGovernedTool(searchTool, {
  control,
  trust: {
    minTrustScore: 500,
    getTrustScore: async (agentId) => {
      // Query your trust registry / AgentMesh trust bridge
      return 750;
    },
  },
  audit: {
    captureData: true,
    sink: async (entry) => {
      console.log(`[AUDIT] ${entry.action} ${entry.toolId}`, entry.hash);
    },
  },
  agentId: "my-agent",
});
```

The ACS manifest declares tool catalogs, intervention-point bindings, budgets,
content filters, and transforms. `createGovernedTool` uses
`AgentControl.runTool`, so deny, escalate, and transform behavior stays
consistent with every other ACS host.

### Use trust and audit individually

```typescript
import { trustGate, auditMiddleware } from "@agentmesh/mastra";

// Trust only
const trust = trustGate({
  minTrustScore: 700,
  getTrustScore: async (agentId) => fetchTrustScore(agentId),
});

const verification = await trust.verify("agent-42");
console.log(trust.getTier(verification.trustScore)); // "trusted"

// Audit only
const audit = auditMiddleware({ captureData: true, maxEntries: 10000 });
await audit.record({ toolId: "search", agentId: "bot-1", action: "invoke" });

const { valid } = await audit.verifyChain(); // true if no tampering
```

## API

### `trustGate(config)`

| Option | Type | Description |
|--------|------|-------------|
| `minTrustScore` | `number` | Minimum score (0-1000) to allow execution |
| `getTrustScore` | `function` | Async function returning agent's trust score |
| `onTrustFailure` | `function` | Optional callback when trust check fails |

### `auditMiddleware(config)`

| Option | Type | Description |
|--------|------|-------------|
| `captureData` | `boolean` | Include input/output in audit entries |
| `sink` | `function` | Custom async audit sink |
| `maxEntries` | `number` | Max in-memory entries (default: 10,000) |

### `createGovernedTool(tool, options)`

Wraps a Mastra tool with ACS policy enforcement, trust, and audit. `control` is
required. Optional fields are `trust`, `audit`, `agentId`, and `snapshot`.

## Migration from the removed local policy object

The package no longer accepts its local policy object. Move every constraint
into an ACS manifest and construct `AgentControl` from that manifest. Passing
the removed object is a TypeScript compile error rather than a best-effort
translation.

## Trust Score Tiers

| Score | Tier | Meaning |
|-------|------|---------|
| 900-1000 | Verified Partner | Cryptographically verified, full access |
| 700-899 | Trusted | Established track record |
| 500-699 | Standard | Default for new agents |
| 300-499 | Probationary | Limited access, under observation |
| 0-299 | Untrusted | Blocked from sensitive operations |

## Part of AgentMesh

This package is part of the [AgentMesh](https://github.com/microsoft/agent-governance-toolkit) ecosystem — a trust layer for multi-agent systems with cryptographic identity, zero-trust verification, and runtime governance.

## License

MIT

## Fork 安全依賴安裝（Windows）

本 fork 的 locked Mastra 開發／驗收 graph 固定 core 1.37.1。provider-utils v5／v6
alias 使用官方 3.0.28／4.0.33；legacy ui-utils 仍需 provider-utils 2.2.8 的同步
`safeParseJSON`，因此由本地 hash-bound backport 修正 GHSA-866g-f22w-33x8。
此為本 fork source checkout 的 locked 開發 graph 修補，非官方 2.x 新版本，
也不是已發布 npm package 的修補。tarball 維持僅 `dist` 的契約，沒有 install／postinstall
hook，消費者不繼承本專案 overrides；peer 範圍也不保證與此 locked graph 相同。

```powershell
npm ci --ignore-scripts
npm run patch:dependencies
node scripts/patch-provider-utils.mjs --check
npm run build
npm run lint
npm test
```

`npm ci` 不會自動套用 backport；source checkout 必須明確執行上述 patch／check。
build、lint、test 的 source pre-hook 也會套用並驗證，未知版本、原始檔
或 patch 雜湊會 fail closed；不要跳過 hook／verify 或直接使用未驗證的 node_modules。
Windows job 執行相同安裝契約。修補不改 package version 或 npm registry integrity。

backport 參照 [官方修補](https://github.com/vercel/ai/commit/6a436e3)，在兩個 module
format 的三個 buffered JSON／JSON-error／status-error handlers 使用共享讀取器。
本 fork 將上限設為 **8 MiB 原始 bytes**：Content-Length 僅提前拒絕，缺少、無效或
低報的 header 仍按串流 byteLength 計量；超限取消，正常／abort／讀取錯誤後均釋放
reader lock。UTF-8 解碼在受限 buffer 完成後進行，超過上限的合法大型 response
也會被拒絕。未改 streaming SSE／JSON-stream 或 binary handler 的既有契約。

官方 2.x 尚無 patched artifact，因此 npm audit／Dependabot 仍會依原版號報告 raw
low；本地 backport 的行為證據與 raw alerts 必須分別記錄，不能宣稱官方清冊歸零。
升級 core／ui-utils 或移除此 backport 前，須重新核對官方 patch 與 API 並驗收。
