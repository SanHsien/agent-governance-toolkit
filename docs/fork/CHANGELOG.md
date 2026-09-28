# 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。
本檔只記錄**本 fork 的維護歷史**（2026-08-28 起）；上游
[`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit)
的產品演進見其自身 [`CHANGELOG.md`](../../CHANGELOG.md) 與 [`docs/fork/UPSTREAM.md`](UPSTREAM.md) 的審查清冊。

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
