# Fork 維護說明

本 repo fork 自 [`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit)，
沿用 MIT License 與完整 Git 歷史。產品名是 **Agent Governance Toolkit（AGT）**：在 LangChain、CrewAI 等框架的 Tool / API 呼叫外層，用確定性政策引擎與熔斷控管權限、Token 預算與稽核，而不是靠 prompt 勸 Agent 守規矩。

## 為什麼維護 fork

- 保留上游持續更新的政策引擎、零信任身份、沙箱、SRE、LangChain／CrewAI 等 adapter，以及多語言 SDK。
- 採 Windows-first 維護：Windows 11 + PowerShell 是主要開發、除錯與完整驗收環境。
- 繁中維護規則放本檔；根目錄 `README.md` 必須保持上游英文產品說明（產品測試與文件契約）。
- 建立可重現的 Windows fork gate、fork CI，以及逐筆審查的上游追蹤。
- 把會發 PyPI／npm／NuGet／GHCR、部署 GitHub Pages、自動合併 Dependabot、以及每日巨型產品 CI 的 workflow 隔離在官方 repo。

**回貢判準：修的是上游的 bug 就送回去；這裡獨創的文件／Windows 維護骨架留在這裡。**
回貢前必須在當次對話取得維護者明確同意；「fork」「建開發環境」「開 PR」都不是同意。

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `README.md` | 上游英文產品說明 + 頂部 fork overlay。繁中維護在本檔／`REVIEW.md` |
| `AGENTS.md` / `CLAUDE.md` | 開頭加上本 fork overlay；下文仍是上游產品規則 |
| `SECURITY.md` / `CONTRIBUTING.md` | 開頭 overlay：本線 PR／overlay 問題走 SanHsien；產品漏洞與產品貢獻仍指向上游 |
| `NOTICE.md` | 本 fork 的來源與授權說明。根目錄 `NOTICE` 仍是上游第三方清單 |
| `tools/dev_check.ps1` | Windows 本機一鍵 fork gate：維護工具的檢查，加上**本 fork 分歧產品碼**的測試（目前是 `agent-os` 的 MCP 認證強制）。不安裝產品套件，只需 `requirements-dev.txt` |
| `.github/workflows/fork-maintenance.yml` | fork 文件與連結檢查，以及分歧產品碼的測試——上游 CI 鎖在 `microsoft/` 名下，那些檔只有這裡測得到。分支保護的兩個必要檢查就是它的 ubuntu／windows job |
| `.github/workflows/upstream-check.yml` | 每週對 `upstream/main` 做未審查 commit 檢查 |
| 上游 CI／發佈／Pages／AI 掃描／自動合併等 workflow | 加上只在官方 `microsoft/agent-governance-toolkit` 執行的 guard |
| `docker-compose.yml` | dashboard 埠綁 `127.0.0.1:8501` |
| `examples/demos/openclaw-governed/docker-compose.yaml` | sidecar 埠綁 `127.0.0.1:8081` |
| `docs/fork/` | Windows 開發、上游審查、決策、本線 changelog |

產品程式（`agent-governance-python/`、各語言 SDK、`policy-engine/`、上游 `docs/`）以上游為準，除非 `REVIEW.md`／`docs/fork/DECISIONS.md` 已記錄 fork overlay。目前 overlay：根目錄 dashboard 與 OpenClaw demo 的 Compose 埠綁 `127.0.0.1`。

## 分支與 remote（單一最新原則）

- **單一最新原則**：本 fork 在 GitHub 上嚴格保持**單一最新分支（`main`）、單一最新 tag（如 `v5.0.0`）、單一最新 release**。
- `origin/main`：SanHsien 維護線，也是 GitHub 上唯一允許存在的分支。
- 檢查遠端分支**必須直接查詢 GitHub API**（例如 `gh api /repos/SanHsien/<repo>/branches`），不能只憑本地未 fetch/prune 的 `git branch -r`，以防漏掉 Dependabot 等背景開立的遠端分支。
- 上游同步時，舊的歷史 tags 不要全數鏡射推送到 `origin`；`origin` 上僅保留最新一個版本 tag。
- 日常修改在本機跑 gate 後直接推 `origin/main`。
- `upstream/main`：microsoft 原始專案，只追蹤、不推送。
- Dependabot 或外部 fork 的變更走 PR，讀 diff 並通過 CI 後再合併。**不自動合併。**

不要 `git push upstream`。同步方式見 [`docs/fork/UPSTREAM.md`](docs/fork/UPSTREAM.md)。

上游更新英文 `README.md` 時，保留頂部 overlay，不要把產品說明改寫成維護索引。繁中維護差異寫在本檔。來源 credit 留在 README 與 [`NOTICE.md`](NOTICE.md)。

## 換一台電腦怎麼開發

```powershell
git clone https://github.com/SanHsien/agent-governance-toolkit.git
cd agent-governance-toolkit
# `gh repo clone` 已會加上 `upstream` remote；若沒有：
# git remote add upstream https://github.com/microsoft/agent-governance-toolkit.git
pwsh -NoProfile -File tools\bootstrap_dev.ps1
```

這是 fork 文件與 guard 的硬閘門，不是完整產品回歸。產品行為變更再依 [`docs/fork/DEVELOPMENT.md`](docs/fork/DEVELOPMENT.md) 安裝對應套件。

只想使用產品、不開發時，請走上游官方來源：

```powershell
pip install "agent-governance-toolkit[full]"
```

不要把 `tools/`、`docs/fork/`、`.github/workflows/fork-maintenance.yml` 當成產品裝包。本 fork **不發** PyPI、npm、NuGet 或容器映像。

## 對外邊界：PR 只打本 fork

- **PR、push、release 一律指向 `SanHsien/agent-governance-toolkit`。** 對上游 `microsoft/agent-governance-toolkit` 開 PR、push 或發 release
  需要維護者在當次對話明確同意回貢。
- 根因是機制不是粗心：`gh` 在 fork clone 的**預設 repo 就是上游**。每個 clone 先跑一次
  `gh repo set-default SanHsien/agent-governance-toolkit`。
- 開 PR 仍明寫 `gh pr create --repo SanHsien/agent-governance-toolkit --base <分支> --head <分支>`，並**讀輸出的 URL**，
  owner 必須是 `SanHsien`。
- 2026-08-22 一天內兩個工作階段各誤開一個上游 PR（`lidge-jun/opencodex#2373`、
  `hamanpaul/paulsha-cortex#787`）。

## 相關工具：治理的是不同範圍

本工具治理的是**上線後自主運行的 agent**——政策強制、零信任身分、沙箱執行與可稽核記錄。
維護者另外有一組五層的 repo，治理的是**替人寫程式的 coding agent**，兩者範圍不同、不要混為一談：

| 層 | Repo |
| --- | --- |
| 供應鏈 | [SkillSpector](https://github.com/SanHsien/SkillSpector) |
| 派工決策 | [agent-advisor](https://github.com/SanHsien/agent-advisor) |
| 動作攔截 | [harness-guard](https://github.com/SanHsien/harness-guard) |
| 產出品質 | [ai-quality-gates](https://github.com/SanHsien/ai-quality-gates) |
| 交付流程 | [paulsha-cortex](https://github.com/SanHsien/paulsha-cortex) |

## 審查紀錄

本輪倉庫審查見 [`REVIEW.md`](REVIEW.md)。
