# 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。
本檔只記錄**本 fork 的維護歷史**（2026-08-28 起）；上游
[`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit)
的產品演進見其自身 [`CHANGELOG.md`](../../CHANGELOG.md) 與 [`docs/fork/UPSTREAM.md`](UPSTREAM.md) 的審查清冊。

## 2026-08-28

### 新增

- Windows-first 維護型 fork overlay：`FORK.md`、`NOTICE.md`、`REVIEW.md`、`CLAUDE.md`、`docs/fork/`、`tools/dev_check.ps1`、上游檢查與連結檢查。
- `fork-maintenance.yml`、`upstream-check.yml`、`dependency-freshness.yml`。
- 上游 CI／發佈／Pages／自動合併／AI 掃描類 workflow 的官方-repo-only guard。
- 根目錄 `README.md`、`AGENTS.md`、`SECURITY.md`、`CONTRIBUTING.md` 頂部 fork overlay；繁中維護入口在 `FORK.md`。

### 修正

- 根目錄 dashboard 與 OpenClaw demo 的 Compose 發佈埠改綁 `127.0.0.1`。
- `.gitignore` 加 `.agt/`。
- `SECURITY.md` 寫明 Compose overlay 與殘餘風險。
