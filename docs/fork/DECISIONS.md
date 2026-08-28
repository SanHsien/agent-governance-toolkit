# 維護決策

## 2026-08-28：建立 Windows-first 維護型 fork

**決定**：fork `microsoft/agent-governance-toolkit`，保留 MIT 與完整歷史。本線與上游預設分支都是 `main`。本線聚焦 Windows 開發 gate、fork CI、workflow 官方-repo 閘門，以及逐筆審查的上游追蹤。根目錄 `README.md` 保持上游英文，繁中維護入口在 `FORK.md`。

**理由**：AGT 已是可用的 Agent 安全核心（政策引擎、Token 預算熔斷、LangChain／CrewAI adapter、OWASP Agentic Top 10）。缺的是 Windows 11 上可重現的開發／驗收骨架，以及不誤發官方套件的 fork 邊界。直接用上游 repo 難以長期記錄 fork 取捨。英文 README 是產品文件與版本橫幅契約（見上游 `AGENTS.md`），不改寫成繁中落地頁。

**限制**：

- 不把 fork 包裝成原創專案，不移除 Microsoft 作者、商標說明與官方連結。
- 不發佈 PyPI、npm、NuGet、GHCR 或 GitHub Pages 文件站。
- 維護 gate 不安裝產品依賴（LangChain、CrewAI、完整 `[full]` extra）。
- 上游更新必須逐筆審查。
- 不自動合併 Dependabot。

## 2026-08-28：上游 workflow 全部加上游 repo 閘門

**決定**：除本線新增的 `fork-maintenance.yml`、`upstream-check.yml`、`dependency-freshness.yml` 外，既有 GitHub Actions 都加上 `github.repository == 'microsoft/agent-governance-toolkit'`。包含 `ci.yml`、`publish.yml`、`publish-containers.yml`、`docs.yml`、`auto-merge-dependabot.yml`，以及 AI 掃描、welcome、stale、CodeQL、ClusterFuzzLite 等。

**理由**：上游 `ci.yml` 是跨語言巨型矩陣且有每日 cron；`docs.yml` 會部署 GitHub Pages；`publish.yml` 會發登錄庫；`auto-merge-dependabot.yml` 違反本線「讀 diff 才合併」；`pull_request_target` 類 workflow 在 fork 上風險更高。閘門讓那些工作在本 fork 直接跳過。同步上游時若衝突，保留閘門。

## 2026-08-28：依賴新鮮度只看維護工具

**決定**：`tools/check_dependency_freshness.py` 只讀 `requirements-dev.txt`。產品 pin 在各套件 `pyproject.toml`，交給 Dependabot。

**理由**：上游有數十個 Python／npm／NuGet／crate pin。每月拿它們對 PyPI 會永遠紅燈。Dependabot 已能對產品依賴開 PR；維護工具的地板檢查保持可讀。

## 2026-08-28：不啟用 Dependabot 自動合併

**決定**：Dependabot 只開 PR；CI 與人工讀 diff 通過後才合併。上游 `auto-merge-dependabot.yml` 已閘在官方 repo。

**理由**：產品依賴會改治理語意與發佈面，不適合自動合併。本線品質關卡禁止 loop／gate 自動合併。

## 2026-08-28：日常直接推 main

**決定**：日常修改在本機跑 `tools\dev_check.ps1` 後直接推 `origin/main`。Dependabot 與外部貢獻仍走 PR，合併前讀 diff。

**理由**：對齊其他 SanHsien 維護 fork。產品測試仍在上游 `ci.yml`；本線 gate 是維護骨架。

## 2026-08-28：不改產品 docker-compose 或 SDK 預設

**決定**：本輪不硬化 `docker-compose.yml`、不改 `govern()` 預設政策、不改各語言 SDK。

**理由**：Compose 是上游開發容器（dashboard 走 profile）。產品預設屬上游契約；本輪只加維護骨架。殘餘風險寫進 `REVIEW.md`。
