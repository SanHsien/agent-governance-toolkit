# Repository review（Windows-first）

- Review date: 2026-08-28
- Review baseline: `f824c1dc`（第一輪 overlay）→ 本輪再修可修項
- Remediation: 同日 fork-local overlay（不回貢）
- Upstream reviewed through: `46463ef8689433817fcc0c582a7881f515d4df15`
- Primary environment: Windows 11、PowerShell、Python 3.14.7（本機 gate）；產品執行建議 `pip install "agent-governance-toolkit[full]"`
- Status: 審查可修 findings 已關。R-05、R-08、R-09 接受。不回貢。

## 結論

這個 fork 適合作為 Windows 本機、給 Agent 維護的 AGT 開發線。產品行為跟隨 `microsoft/agent-governance-toolkit` `46463ef`，再加上本線 overlay：dashboard 與 OpenClaw demo 埠綁 `127.0.0.1`、`.agt/` 不進 git、發佈／巨型 CI／自動合併關在官方 repo。

不把 fork 當成第二個官方產品 repo。PyPI `agent-governance-toolkit`、npm `@microsoft/agent-governance-sdk`、NuGet `Microsoft.AgentGovernance`、文件站 microsoft.github.io 仍屬上游。本線 Windows gate **不安裝** 產品 extra，因此 **不能** 證明 LangChain／CrewAI tool call 已在這台機器上被攔截。

## 本輪實證

### 審查當下（`f824c1dc`）

```text
git rev-parse HEAD
→ f824c1dc chore: add Windows-first fork overlay

pwsh -NoProfile -File tools\dev_check.ps1（修正前）
→ 30 passed、WINDOWS DEV CHECK GREEN

實查（不是只讀 README）：
- 根目錄 docker-compose.yml dashboard 當時 `"8501:8501"`，Streamlit `--server.address=0.0.0.0`
- examples/demos/openclaw-governed/docker-compose.yaml 當時 `"8081:8081"`，`HOST=0.0.0.0`
- 套件樹裡另有多份 example Compose 聽 0.0.0.0（Grafana／Grafana 範例），不是本機預設入口
- 產品 CLI／observability 預設 `--host 0.0.0.0`（上游契約）
- 維護工具無 os.system／shell=True／eval(／exec(
- 上游 workflow 已全部官方-repo guard；本線三支 workflow Action SHA 已 pin
```

**沒有**用 Docker 啟動 dashboard，**沒有**對 LangChain／CrewAI 跑真實 LLM。

### 修正後

```text
pwsh -NoProfile -File tools\dev_check.ps1
→ 31 passed、WINDOWS DEV CHECK GREEN
```

## 已修 findings

| ID | 嚴重度 | 做了什麼 |
|---|---|---|
| R-01 | P2 | fork clone 預設 `gh` 打向上游 → `FORK.md`、`AGENTS.md` overlay、`.cursor/rules/no-upstream-pr.mdc` |
| R-02 | P1 | 發佈／Pages／自動合併會在 fork 上跑 → 上游 workflow 官方-repo guard |
| R-03 | P2 | 無 Windows 一鍵 gate → `tools/dev_check.ps1`、`tools/bootstrap_dev.ps1` |
| R-04 | P2 | 無上游水位 → `tools/upstream_baseline.json`、`docs/fork/UPSTREAM.md` |
| R-06 | P2 | 根目錄 dashboard 埠改 `127.0.0.1:8501`；容器內仍聽 `0.0.0.0` |
| R-07 | P2 | OpenClaw demo sidecar 埠改 `127.0.0.1:8081` |
| R-10 | P3 | `.gitignore` 加 `.agt/` |
| R-11 | P3 | `SECURITY.md`／`docs/fork/DEVELOPMENT.md` 寫明 Compose overlay 與殘餘風險 |
| R-12 | P3 | 契約測試鎖 loopback 埠綁、`.agt/`、安全文件 |

## 接受、不改契約

| ID | 嚴重度 | 處理 |
|---|---|---|
| R-05 | P3 | 產品 Python 是 3.10+；Windows gate 用 3.14。執行環境事實，不是 bug |
| R-08 | P3 | 產品 CLI／模組預設 `--host 0.0.0.0`。改 SDK 會每次上游同步衝突，也不是本機一鍵入口 |
| R-09 | P3 | 套件樹裡 Grafana／uvicorn example Compose 仍聽 `0.0.0.0`。那些不是 `docker compose --profile dashboard` 預設路徑；要跑再各自審 |
| R-13 | P3 | 英文 `README.md`。產品文件與版本橫幅契約；繁中在 `FORK.md` |
| R-14 | P3 | 已閘門上游 workflow 的 Action pin 維持現狀。本 fork 不會跑那些 job |

## 已檢查、不列為 finding

- `LICENSE` 為 MIT；`NOTICE.md` 保留 Microsoft 作者；根目錄 `NOTICE` 是上游第三方清單。
- `gh repo set-default --view` → `SanHsien/agent-governance-toolkit`。
- Dependabot 只開 PR。新鮮度只看 `requirements-dev.txt`。
- 生產程式沒有把 `eval(`／`shell=True` 當執行路徑；出現處是偵測規則、對抗樣本或測試。
- Overlay Python 在 `tools/`，用 `tools/pytest.ini`，不會被上游各套件 pytest 掃進去。
- `fork-maintenance.yml`／`upstream-check.yml`／`dependency-freshness.yml` 的 checkout／setup-python 已 pin SHA。

## 尚未宣稱範圍

- **沒有**用 Docker 啟動 dashboard 或 OpenClaw sidecar。
- **沒有**對 LangChain／CrewAI 跑真實 LLM tool call。
- **沒有**跑上游完整 `ci.yml`（已閘在官方 repo）。
- **沒有**發佈任何套件或容器。
- **不宣稱** 已把 overlay 送回上游。
