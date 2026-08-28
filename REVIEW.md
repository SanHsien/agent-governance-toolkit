# Repository review（Windows-first）

- Review date: 2026-08-28
- Review baseline: `46463ef8689433817fcc0c582a7881f515d4df15`（fork 起點；overlay 提交後再補 SHA）
- Remediation: 同日 fork-local overlay（不回貢）
- Upstream reviewed through: `46463ef8689433817fcc0c582a7881f515d4df15`
- Primary environment: Windows 11、PowerShell、Python 3.14（本機 gate）；產品執行建議 `pip install "agent-governance-toolkit[full]"`
- Status: 維護骨架可跑。R-01～R-04 已在本線修。R-05（產品 Python 3.10+ vs gate 3.14）接受。

## 結論

這個 fork 適合作為 Windows 本機、給 Agent 維護的 AGT 開發線。產品行為跟隨 `microsoft/agent-governance-toolkit` `46463ef`。本線 overlay：繁中維護入口、Windows gate、上游追蹤，以及把發佈／巨型 CI／自動合併關在官方 repo。

不把 fork 當成第二個官方產品 repo。PyPI `agent-governance-toolkit`、npm `@microsoft/agent-governance-sdk`、NuGet `Microsoft.AgentGovernance`、文件站 microsoft.github.io 仍屬上游。本線 Windows gate **不安裝** 產品 extra，因此 **不能** 證明 LangChain／CrewAI tool call 已在這台機器上被攔截。

## 本輪實證

### 審查當下（`46463ef`）

```text
git rev-parse HEAD
→ 46463ef8689433817fcc0c582a7881f515d4df15

upstream tag
→ v4.1.0 已在歷史中；VERSION 檔為 5.0.0
```

實查（不是只讀 README）：

- 上游 workflow 在 overlay 後都帶 `github.repository == 'microsoft/agent-governance-toolkit'`（契約測試會鎖住）。
- `auto-merge-dependabot.yml` 同樣閘在官方 repo。
- `docs.yml` 部署 GitHub Pages，已閘。
- `publish.yml` / `publish-containers.yml` 已閘。
- 根目錄 `NOTICE` 是上游第三方清單；本 fork 說明在 `NOTICE.md`。

## 已修 findings

| ID | 內容 | 處理 |
| --- | --- | --- |
| R-01 | fork clone 預設 `gh` 打向上游 | `FORK.md`、`AGENTS.md` overlay、`.cursor/rules/no-upstream-pr.mdc` |
| R-02 | 發佈／Pages／自動合併會在 fork 上跑 | 上游 workflow 官方-repo guard |
| R-03 | 無 Windows 一鍵 gate | `tools/dev_check.ps1`、`tools/bootstrap_dev.ps1` |
| R-04 | 無上游水位 | `tools/upstream_baseline.json`、`docs/fork/UPSTREAM.md` |

## 接受、不改契約

| ID | 內容 | 理由 |
| --- | --- | --- |
| R-05 | 產品 Python 是 3.10+；Windows gate 用 3.14 | gate 只跑維護工具。不把產品上限改成 3.14 |
| R-06 | `docker-compose.yml` dashboard 聽 `0.0.0.0` | 上游開發容器，走 `dashboard` profile。本輪不改產品 Compose |
| R-07 | 英文 `README.md` | 產品文件與版本橫幅契約；繁中在 `FORK.md` |

## 尚未宣稱範圍

- 未在本機對 LangChain／CrewAI 跑真實 LLM tool call。
- 未跑上游完整 `ci.yml`（已閘在官方 repo）。
- 未發佈任何套件或容器。
