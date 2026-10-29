# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `a515cd224d7f` 查的快照，開工前先重查 GitHub。

## 現況
這是 Agent Governance Toolkit 的 Windows 維護型 fork，提供代理執行期政策、身分與沙箱治理（[FORK.md](FORK.md)）。2026-10-29 `gh` 查詢顯示 Fork maintenance、Fork product Windows、Upstream check 最近結果成功；Dependabot 仍有 deepmerge 的低風險告警 2 筆，尚無修補版，本次重查確認仍只經 Jest 開發依賴引入，理由與證據見 [DECISIONS](docs/fork/DECISIONS.md#2026-10-29deepmerge-延後項目重查)；Code scanning 未查到分析，不能當成零告警（2026-10-29 `gh` 查詢）。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 盤點 Windows gate 是否能建出 policy Python SDK 原生擴充 | 待採用修正需 `_native` 才能驗證 | 按 SDK 開發指引在隔離環境建置，確認可匯入 `_native` 並執行 `tests/test_orchestration.py`；失敗需留下確切前置依賴與錯誤，不宣稱已採用修正 | Codex | docs/fork/DECISIONS.md:703；上游 PR #4428 |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 採用 run_tool 提前拒絕修正 | 上游合併，或已能建出 `_native` 並驗證當前 PR head | 先證明未綁定 post_tool_call 時工具不被執行；回歸與 SDK 測試通過，採用裁決可追溯 | Codex | docs/fork/DECISIONS.md:703；上游 PR #4428 |
| 重新裁決既有 WATCH 提案 | 各項已記錄的合併、遷移說明、實機可測或威脅模型條件成立 | 逐項連回既有裁決，只採用能在 Windows 重現問題且修後通過的變更；不重開已採用項目 | Claude Opus | `docs/fork/DECISIONS.md:639-645` |
| 重新評估 workflow 生成器同步 | 生成器可保留 fork guard，且無符號連結權限時測試可合理處理 | `generate_workflows.py --check` 通過，重新生成前後所有官方 repo guard 保留，相關測試通過 | Codex | docs/fork/DECISIONS.md:679 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 無修補版時替換 deepmerge API 或 dismiss 告警 | 依賴用途與延後理由已在 DECISIONS.md 的 2026-10-29 重查段記錄 | 修補版、jest-config 移除依賴、API 提供 first_patched_version，或依賴進入 runtime |
| 把上游產品 ROADMAP 的所有功能當成本 fork 承諾 | docs/ROADMAP.md 是上游產品方向；fork 維護邊界見 FORK.md | 維護者明確選定功能與 Windows 驗收範圍 |
| 為 No common ancestor 改寫歷史或強推；啟用官方發布流程 | 已知歷史形態不影響逐筆審查；發布與 Pages 被 FORK.md 隔離 | 維護者另行授權歷史或發布政策變更 |

## 維護方式
每週依 [上游流程](docs/fork/UPSTREAM.md) 與 `tools/upstream_baseline.json` 查未審 commit／PR／issue；Upstream check 失敗先確認新增待審項目，採用須有裁決與 Windows 測試。
依賴安全更新逐筆審 diff，執行 `pwsh -NoProfile -File tools/dev_check.ps1` 與受影響產品 gate；只操作 SanHsien 維護線，發布界線依 FORK.md。