# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況快照：2026-11-25，工作分支基準 `d2c294b8`；上游 main `3233be2338816257700a8dbdf531a21b9f359582`。

## 現況
這是 Agent Governance Toolkit 的 Windows 維護型 fork（[FORK.md](FORK.md)）。2026-11-25 在工作分支基準 `d2c294b8` 重查 Dependabot open alerts：27 筆（medium 23、low 4），取代 2026-11-23 的 31 筆歷史快照。5 個告警 manifest 均與當日上游 main 不同，按本輪逐檔定義皆為 fork-owned，upstream-owned 為 0。此次在 MCP proxy、MCP server 與 Mastra 的 lockfile 修補 20 筆對應依賴，7 筆延後；ruff 下限升為 0.17.6。這是本地修補與分類結果，未推送，不能宣稱 GitHub 告警已關閉或遠端 CI 已轉綠。逐筆編號、檔案比對與驗證見 [DECISIONS](docs/fork/DECISIONS.md#2026-11-25dependabot-分流與-ruff-下限更新)。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 上游 #4529 合併後，把 `TrustGatedMCPClient` 的 server DID 探索與註冊表驗證換成上游版本，保留 fork 的 server 端與 `connect()` 強化 | 上游合併 #4529（目前仍 open，head `d2009cc7`，CHANGES_REQUESTED）。2026-11-11 的獨立覆核修正（B1–B5）已讓 fork 的 `TrustGatedMCPServer` 與 client 撤銷／型別判斷超出 #4529：#4529 只改 client，不涵蓋 server、撤銷與 `is not None`，所以不能整檔取上游 | 取上游 `server_identity.py` 與 client registry 路徑；`TrustGatedMCPServer`、`_verified_peer`、先撤銷與連線綁定保留；`test_mcp_server_verification.py`、`test_mcp_integration.py`、`test_mcp_identity_enforcement.py` 全過，FORK.md 差異表該列改成只描述剩下的差異 | Claude Opus | `docs/fork/DECISIONS.md` 2026-11-11（含合併步驟）；`agent-governance-python/agent-mesh/src/agentmesh/integrations/mcp/__init__.py` |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 處理延後的 7 筆 Dependabot：Node SDK 的 hono／@hono/node-server 6 筆，Cloud Board opentelemetry-api 1 筆 | Node SDK 可取得完整 Windows 原生建置與 OPA 驗收；Cloud Board 可同步升級 OpenTelemetry SDK／semantic-conventions／instrumentation 並完成服務測試 | Node SDK `npm run test:ci` exit 0；Cloud Board 解析無衝突且服務測試通過，再核對告警狀態 | Codex | `docs/fork/DECISIONS.md` 2026-11-25；此輪未推送 |
| `fork-product-windows` 加 policy Python SDK job | 再次動到 `policy-engine/sdk/python` 的 fork 分歧碼，或維護者要求 | CI 能建出 `_native` 並跑 `test_run_tool_unbound_post.py`、`test_orchestration.py` | Antigravity | `docs/fork/DECISIONS.md` 2026-10-30；`tools/dev_check.ps1` 不裝產品套件 |
| 驗證並採用上游 #4480（india Rego 政策修正）、#4059（快照契約的鍵，破壞性）與 #4486（cmvk 錯誤細節，TypeScript） | 本機或 CI 取得 `opa`（`opa test examples/policies`；#4059 另需能跑 `policy-engine` 的 Cedar 測試與 `sdk/python` 的 `test_host.py`），或能跑 `agent-os-vscode` 的 TypeScript 測試 | 重現舊碼失敗、套用後通過；#4480、#4059 整批取上游版本並跑 `opa test`，#4486 移植；順帶重看 issue #4481、#4485 | Codex | `docs/fork/DECISIONS.md` 2026-11-02 第六輪、2026-11-10 第七輪 |
| 採用上游 #4529（MCP server DID 探索與驗證）以修 issue #4528（`TrustGatedMCPClient` 不驗證伺服器身分） | 上游合併 #4529。現況：fork 已有失敗關閉的最小緩解，且 2026-11-11 起 server 端（B1／B3）、client 撤銷（B4）、型別判斷（B2／B5）也修了，這些 #4529 都不涵蓋；剩下等 #4529 的是 server DID 探索（`_discover_server_did` 仍回傳 `None`）與註冊表簽章驗證。步驟見上方近期表同主題列 | `agent-mesh` 的 `test_mcp_server_verification.py`、`test_mcp_integration.py`、`test_mcp_identity_enforcement.py` 通過，`connect()` 對未驗證的伺服器回傳失敗 | Claude Opus | `docs/fork/DECISIONS.md` 2026-11-10 第七輪、2026-11-11 |
| 處理 issue #4527（OpenCode 外掛 5.0.0 在 OpenCode 2.2.x 載入失敗，V1／V2 外掛契約） | 上游有修正 PR，或本機能安裝 OpenCode 2.2.x 重現 | 重現載入錯誤，套用後外掛載入且 `agt_policy_status` 註冊 | Codex | `docs/fork/DECISIONS.md` 2026-11-10 第七輪；`agent-governance-opencode/src/index.mjs:247` |
| 處理 issue #4559（protocol-facets 的 UNKNOWN 動詞契約在 Go、TypeScript 不一致：Go 的 `protocol_facets.go` 仍帶出表名，TypeScript 的 CTE 分支未歸為 UNKNOWN） | 上游開出修正 PR，或維護者確認跨 port 契約 | 重現 Go 與 TypeScript 的 UNKNOWN 輸出，先紅後綠修正；契約以 TypeScript JSDoc 與 `UNKNOWN_SQL_FACETS` 為準 | Claude | `docs/fork/DECISIONS.md` 2026-11-11 第八輪；`agent-governance-golang/packages/agentmesh/protocol_facets.go:252`、`agent-governance-typescript/src/protocol-facets.ts:166` |
| 重新裁決既有 WATCH 提案 | 各項已記錄的合併、遷移說明、實機可測或威脅模型條件成立 | 逐項連回既有裁決，只採用能在 Windows 重現問題且修後通過的變更；不重開已採用項目 | Claude Opus | `docs/fork/DECISIONS.md:639-645` |
| 重新評估 workflow 生成器同步 | 生成器可保留 fork guard，且無符號連結權限時測試可合理處理 | `generate_workflows.py --check` 通過，重新生成前後所有官方 repo guard 保留，相關測試通過 | Codex | docs/fork/DECISIONS.md:679 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 無修補版時替換 deepmerge API（告警 #292／#286 已依 2026-11-08 決定 dismiss） | 開發依賴、無修補版；用途與理由見 DECISIONS.md 的 2026-10-29 重查段與 2026-11-08 段 | 修補版、jest-config 移除依賴、API 提供 first_patched_version，或依賴進入 runtime |
| 把上游產品 ROADMAP 的所有功能當成本 fork 承諾 | docs/ROADMAP.md 是上游產品方向；fork 維護邊界見 FORK.md | 維護者明確選定功能與 Windows 驗收範圍 |
| 為 No common ancestor 改寫歷史或強推；啟用官方發布流程 | 已知歷史形態不影響逐筆審查；發布與 Pages 被 FORK.md 隔離 | 維護者另行授權歷史或發布政策變更 |

## 維護方式
每週依 [上游流程](docs/fork/UPSTREAM.md) 與 `tools/upstream_baseline.json` 查未審 commit／PR／issue；Upstream check 失敗先確認新增待審項目，採用須有裁決與 Windows 測試。
依賴安全更新逐筆審 diff，執行 `pwsh -NoProfile -File tools/dev_check.ps1` 與受影響產品 gate；只操作 SanHsien 維護線，發布界線依 FORK.md。
