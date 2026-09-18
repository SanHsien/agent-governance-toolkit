# Fork 維護說明

本 repo fork 自 [`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit)，
沿用 MIT License 與完整 Git 歷史。產品名是 **Agent Governance Toolkit（AGT）**：在 LangChain、CrewAI 等框架的 Tool / API 呼叫外層，用確定性政策引擎與熔斷控管權限、Token 預算與稽核，而不是靠 prompt 勸 Agent 守規矩。

## 為什麼維護 fork

- 保留上游持續更新的政策引擎、零信任身份、沙箱、SRE、LangChain／CrewAI 等 adapter，以及多語言 SDK。
- **僅支援 Windows 作業系統**：Windows 11 / Windows Server + PowerShell 是唯一開發、除錯與完整驗收環境，移除非必要之跨平台冗餘。
- **語言支援方針**：本儲存庫依維護原則僅保留繁體中文與英文文件，以繁體中文為主。根目錄 `README.md` 為繁體中文主說明檔，英文規格請見 [`README.en.md`](README.en.md)。
- 建立可重現的 Windows fork gate、fork CI，以及逐筆審查的上游追蹤。
- 把會發 PyPI／npm／NuGet／GHCR、部署 GitHub Pages、自動合併 Dependabot、以及每日巨型產品 CI 的 workflow 隔離在官方 repo。

**回貢判準：修的是上游的 bug 就送回去；這裡獨創的文件／Windows 維護骨架留在這裡。**
回貢前必須在當次對話取得維護者明確同意；「fork」「建開發環境」「開 PR」都不是同意。

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `README.md` / `README.en.md` | 根目錄 `README.md` 為繁體中文主說明檔；`README.en.md` 為英文版規格與說明 |
| `AGENTS.md` / `CLAUDE.md` | 開頭加上本 fork overlay，明定僅支援 Windows 與繁體中文為主；下文仍是上游產品規則 |
| `SECURITY.md` / `CONTRIBUTING.md` | 開頭 overlay：本線 PR／overlay 問題走 SanHsien；產品漏洞與產品貢獻仍指向上游 |
| `NOTICE.md` | 本 fork 的來源與授權說明。根目錄 `NOTICE` 仍是上游第三方清單 |
| `tools/dev_check.ps1` | Windows 本機一鍵 fork gate：維護工具的檢查，加上**本 fork 分歧產品碼**的測試（目前是 `agent-os` 的 MCP 認證強制）。不安裝產品套件，只需 `requirements-dev.txt` |
| `.github/workflows/fork-maintenance.yml` | fork 文件與連結檢查，以及分歧產品碼的測試（僅支援 Windows，分支保護之必要檢查為 fork gate (windows-latest)） |
| `.github/workflows/upstream-check.yml` | 每週對 `upstream/main` 做未審查 commit 檢查 |
| 上游 CI／發佈／Pages／AI 掃描／自動合併等 workflow | 加上只在官方 `microsoft/agent-governance-toolkit` 執行的 guard |
| `docker-compose.yml` | dashboard 埠綁 `127.0.0.1:8501` |
| `examples/demos/openclaw-governed/docker-compose.yaml` | sidecar 埠綁 `127.0.0.1:8081` |
| `docs/fork/` | Windows 開發、上游審查、裁決、本線 changelog |

產品程式碼（`agent-governance-python/`、各語言 SDK、`policy-engine/`、上游 `docs/`）以上游為準，除非 `REVIEW.md`／`docs/fork/DECISIONS.md` 已記錄 fork overlay。本機 overlay：根目錄 dashboard 與 OpenClaw demo 的 Compose 埠綁 `127.0.0.1`。

## 分支與 remote（單一最新原則）

- **單一最新原則**：本 fork 在 GitHub 上嚴格維持**單一最新分支（`main`）、單一最新 tag（如 `v5.0.0`）、單一最新 release**。
- `origin/main`：SanHsien 維護線，也是 GitHub 上唯一常駐存在的分支。
- 檢查遠端分支**必須直接查詢 GitHub API**（例如 `gh api /repos/SanHsien/<repo>/branches`），不能光憑本地的 fetch/prune 或 `git branch -r`，以防漏看 Dependabot 等服務自動建立的遠端分支。
- 上游同步時，所有歷史 tags 不得以參數全數推送到 `origin`；`origin` 上只保留最新一個版號 tag。
- 平常修改在本地跑 gate 後直接推 `origin/main`。
- `upstream/main`：Microsoft 官方主線，只讀取、不推送。
- Dependabot 打上本 fork 的安全補丁 PR，讀 diff 且通過 CI 後手動合入。**不自動合併。**

不要 `git push upstream`。正常流程見 [`docs/fork/UPSTREAM.md`](docs/fork/UPSTREAM.md)。

上游更新英文 `README.en.md` 時，保持頂部 overlay；不要把產品說明直接替換掉。繁中維護說明集中在本檔。作者 credit 寫在 README 與 [`NOTICE.md`](NOTICE.md)。

## 換一台新電腦怎麼開發

```powershell
git clone https://github.com/SanHsien/agent-governance-toolkit.git
cd agent-governance-toolkit
# `gh repo clone` 會自動加上 `upstream` remote；若沒有：
# git remote add upstream https://github.com/microsoft/agent-governance-toolkit.git
pwsh -NoProfile -File tools\bootstrap_dev.ps1
```
