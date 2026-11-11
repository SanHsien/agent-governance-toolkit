---
title: Fork 維護變更紀錄
last_reviewed: 2026-11-11
owner: agt-maintainers
---

# 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。
本檔只記錄**本 fork 的維護歷史**（2026-08-28 起）；上游
[`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit)
的產品演進見其自身 [`CHANGELOG.md`](../../CHANGELOG.md) 與 [`docs/fork/UPSTREAM.md`](UPSTREAM.md) 的審查清冊。

## 2026-11-11

### 安全修正

- 獨立覆核（另一個模型家族的唯讀審查）在 `agentmesh/integrations/mcp/__init__.py` 發現 5 個既有身分驗證缺口，全數在 fork 修正並以真實 `HandshakeResult` 寫成回歸測試（`tests/test_mcp_identity_enforcement.py`，55 項，修前紅）。逐項設計、與上游 #4529 的關係、行為變更與殘餘風險見 [DECISIONS.md](DECISIONS.md#2026-11-11mcp-身分驗證缺口-b1b5獨立覆核發現fork-修正)。
- B1（高）`invoke_tool` 只對已通過 `verify_client` 的 DID 執行，分數／capability／sponsor 取自驗證結果而非呼叫者自報，`require_human_sponsor` 開始強制（新增選用 `identity_registry`）。B2（高）以 `HandshakeResult.verified is True` 判斷。B3（高）bridge 拒絕為終局、移除 card 分數 fallback。B4（中）`connect()` 先撤銷舊連線、連線綁定已驗證 DID 與 bridge。B5（低）bridge 存在判斷改 `is not None`。
- 對外行為變更：`invoke_tool` 前必須 `verify_client`；無 `trust_bridge` 的 server 拒絕所有 client。

## 2026-11-10

### 同步與修正

- 第七輪上游審查，水位推進至 `48f04e5a`、PR 4540、issue 4528；逐項結論見 [DECISIONS.md](DECISIONS.md#2026-11-10上游審查第七輪d1d0ccea--48f04e5a)。
- 取上游 `agent-discovery` 的 `cli/main.py`、`inventory.py`、`tests/test_cli.py`（#4477 合併版）。
- 移植 15 個上游 open 修正 PR（#4512、#4513、#4521、#4522、#4523、#4531–#4540）與 1 個測試 PR（#4524）；每個修正的新測試在 fork 舊碼失敗、套用後通過。
- `#4059`（快照契約的鍵，破壞性變更）、`#4529`／issue `#4528`（MCP 伺服器身分驗證）、issue `#4527`（OpenCode 外掛契約）記為待辦，條件見 `ROADMAP.md`。

## 2026-10-29

### 維護查核

- 重查 deepmerge 兩筆開放告警與 npm 版本；仍無修補版，兩套件皆只經 Jest 開發依賴引入。延後裁決與實際查核指令記於 [DECISIONS.md](DECISIONS.md#2026-10-29deepmerge-延後項目重查)，不改 manifest／lock、不 dismiss 告警。
- 更新 `REVIEW.md` 的本次查核範圍，從 `ROADMAP.md` 近期表格移除已完成的重查列；保留條件式重看規則。

## 2026-09-12

### 同步與修正

- 合併上游 `upstream/main` 41 個提交至 `0533cea`（含 Claude Code hook 啟動修復 `#3854`、各模組依賴更新等）。
- 引入 PR `#3913`：`OPAEvaluator` 改採 `--stdin-input`，解決 Windows 上缺乏 `/dev/stdin` 造成的靜默拒絕問題（修復 Issue `#3912`）。
- 引入 PR `#3916`：將 `govern(audit_file=...)` 正式接至 `FileAuditSink`，修復稽核檔案無法持久化至磁碟之問題（修復 Issue `#3915`）。
- 引入 PR `#3924`：PolicyRule 條件 DSL 支援 `contains`、`startswith`、`endswith` 運算子，防止 deny 規則靜默失效。
- 引入 PR `#3853`：修復 `CredentialRedactor` 秘鑰後緊接標註後綴時漏遮蔽之安全性缺陷（修復 Issue `#3494`），並修正 Windows 下測試環境變數長度上限相容性。
- 逐一審查並合入 Dependabot PR `#3`（brace-expansion）、PR `#4`（hono）、PR `#5`（@babel/core）、PR `#6`（js-yaml）之安全更新至 `main`。
- 清理遠端已合入之分支，落實 `SanHsien/agent-governance-toolkit` 唯一主分支 `main` 與單一最新 tag/release `v5.0.0`。

## 2026-08-28

### 新增

- Windows-first 維護型 fork overlay：`FORK.md`、`NOTICE.md`、`REVIEW.md`（overlay 快照，不是另一次全庫審查委託）、`CLAUDE.md`、`docs/fork/`、`tools/dev_check.ps1`、上游檢查與連結檢查。
- `fork-maintenance.yml`、`upstream-check.yml`、`dependency-freshness.yml`。
- 上游 CI／發佈／Pages／自動合併／AI 掃描類 workflow 的官方-repo-only guard。
- 根目錄 `README.md`、`AGENTS.md`、`SECURITY.md`、`CONTRIBUTING.md` 頂部 fork overlay；繁中維護入口在 `FORK.md`。

### 修正

- 根目錄 dashboard 與 OpenClaw demo 的 Compose 發佈埠改綁 `127.0.0.1`。
- `.gitignore` 加 `.agt/`。
- `SECURITY.md` 寫明 Compose overlay 與殘餘風險。
