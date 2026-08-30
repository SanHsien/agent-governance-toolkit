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

## 2026-08-28：不改產品 docker-compose 或 SDK 預設

**決定**：本輪不硬化 `docker-compose.yml`、不改 `govern()` 預設政策、不改各語言 SDK。

**理由**：Compose 是上游開發容器（dashboard 走 profile）。產品預設屬上游契約；本輪只加維護骨架。殘餘風險寫進 `REVIEW.md`。

**狀態**：已被下一則推翻（dashboard／OpenClaw 埠改綁 loopback；SDK 預設仍不改）。

## 2026-08-28：審查可修項改在本線 overlay，不回貢

**決定**：推翻上一則「不改 Compose」的限制。本線把根目錄 dashboard 埠改成 `127.0.0.1:8501`，把 OpenClaw demo sidecar 改成 `127.0.0.1:8081`。容器內 `--server.address=0.0.0.0`／`HOST=0.0.0.0` 保留，否則 Docker port mapping 失效。`.gitignore` 加 `.agt/`。`SECURITY.md` 寫明 overlay 與殘餘風險。不改產品 CLI／模組的 `--host 0.0.0.0` 預設。不硬化套件樹裡其他 example Compose。不 pin 已閘門 workflow 的 Action SHA（它們本來就幾乎都 pin 了，且本 fork 不會跑）。不把產品 Python 下限改成 3.14。不回貢上游。

**理由**：維護者要求審查裡可修的都修，且先不考慮回貢。根目錄 Compose 與 OpenClaw demo 是本機一鍵啟動面，對區網暴露沒有好處。SDK 預設與套件範例 Compose 每次上游同步都會衝突，改了也證明不了產品回歸。

## 2026-08-28：日常直接推 main

**決定**：日常修改在本機跑 `tools\dev_check.ps1` 後直接推 `origin/main`。Dependabot 與外部貢獻仍走 PR，合併前讀 diff。

**理由**：對齊其他 SanHsien 維護 fork。產品測試仍在上游 `ci.yml`；本線 gate 是維護骨架。

## 2026-08-29：上游檢查補上 PR 與 issue 兩個面向

**決定**：`check_upstream_updates.py` 補上以 `--state all` 收集上游 PR／issue 的邏輯，
`upstream-check.yml` 補 `GH_TOKEN: ${{ github.token }}`，新增 `tests/test_upstream_updates.py`。
Baseline 既有的水位不動。

**理由**：`docs/UPSTREAM.md` 早就寫著「四個面向都要看」，`upstream_baseline.json` 也記著
`reviewed_pr_through` 與 `reviewed_issue_through`——但**沒有任何程式讀那兩個欄位**，檢查器只比對
commit 水位。那兩個面向不是「查過沒發現」，是根本沒查，而每週的排程報告長得跟查過一樣綠。
這是艦隊層級的問題：24 個 fork 裡 21 個都這樣（`SanHsien/repo-fleet-ops` 的 `docs/INCIDENTS.md`
第十條）。參考實作是 `SanHsien/harness-guard`。

三個性質，缺一不可：

- **`--state all`**：只查 `open` 看不到「開了又關、沒有合併」的 PR，而那正是「上游拒收、但可能對
  本 fork 有價值」的一類——已合併的遲早會經由 commit 抵達，被關掉的永遠不會。
- **`gh` 失敗時回 `None` 不回 `[]`**，報告寫 `Not checked` 並 **fail closed**（exit 2）。
  「沒查到」和「沒有」在綠色報告裡長得一樣，只有一個是真的。
- **`GH_TOKEN`**：`gh` 在 Actions 裡沒有憑證就列舉不到，配上 fail closed 會讓紅燈的意思變成
  「檢查器壞了」而不是「上游有東西」。

**證據**：落地後實跑 `python tools/check_upstream_updates.py`，三個面向都印出水位與待辦數；
本 repo 的 gate 全綠。

**已知代價**：水位以上真的有東西時，每週的 upstream-check 會回 exit 1。那是它該做的事——先前的
綠燈不是「沒有待辦」，是沒有人看。

**觸發條件**：報告列出項目時逐筆讀 diff、把採用／略過理由寫進本檔，然後才推進 baseline 的水位。


## 2026-08-30：上游四個 open PR 的逐筆判定

PR 水位 3845 → 3850。四筆都還沒被上游合併，所以不會經由 commit 軸抵達；逐筆判斷如下。

### 採用：未註冊的 MCP server 在 fallback 路徑繞過 TLS 下限（上游 PR #3849）

**在本 fork 實測重現**（`agent-governance-python/agent-os`，`PYTHONPATH=src`）：

| 呼叫 | 修正前 | 修正後 |
| --- | --- | --- |
| 已註冊的 server ＋ `http://plain/insecure` | **拒絕**（TLS 下限） | 拒絕 |
| **未註冊**的 server ＋ 同一個 `http://` URL | **放行** | 拒絕 |
| 未註冊 ＋ `https://` | 放行 | 放行 |
| 未註冊 ＋ 完全不給 URL | 放行 | 放行 |

也就是說：**allowlist 的鍵打錯一個字，傳輸層下限就等於關掉**——已註冊條目走
`entry.require_tls` 的閘門，落到 `# Fall back to default policy` 的那條路上完全沒有 TLS 檢查。
這是治理工具本身的護欄失效，不是使用體驗問題。

落地照上游：`McpAuthPolicy` 新增 `default_require_tls=True`（fail-closed）、fallback 分支補上
與已註冊條目相同的 scheme 檢查（只認 `https`／`wss`）、`from_yaml` 讀 `default_require_tls`。
**只在真的有給 URL 時才擋**，與已註冊條目的閘門一致，所以不會誤擋那些從不傳 URL 的呼叫端。

測試四條（含上游沒有的「未註冊 ＋ 不給 URL 仍放行」，釘住不誤擋這件事）：
`pytest tests/test_mcp_auth_enforcement.py` 21 passed。

### 採用：OPA timeout 測試的 30ms 太緊（上游 PR #3848）

`policy-engine/core/tests/opa.rs` 的假 opa 執行檔 `sleep 30`（秒），測試要驗的是**逾時路徑**。
30ms 的預算在忙碌的 runner 上可能在行程還沒 spawn 完就到期，那時失敗的是 spawn 而不是逾時，
測到的東西就不是這條測試要測的。改成 500ms——仍遠低於 30 秒，逾時照樣會觸發。

**本 fork 也會踩到**：`.github/workflows/ci.yml` 與 `policy-engine-ci.yml` 都跑
`cargo test --workspace`，而本 fork 的 `opa.rs:254` 就是同一行 30ms。

**驗證限制（照實說）**：本機沒有安裝 cargo（`command -v cargo` 無），所以這一行**沒有在本機
實跑過**，只有靜態核對本 fork 的那行與上游相同、且改動只動一個常數。CI 的 `cargo test` 是它的
權威環境。

### 不引用：#3846 土耳其文翻譯

新增 `docs/i18n/README.tr.md`／`quickstart.tr.md` 並改上游 README 的語言列。本 fork 沒有
`docs/i18n/` 目錄，README 也是本線自己的版本。維護一份自己讀不懂、也無法審校的翻譯，
只會變成長期漂移的死文件。

**觸發條件**：上游合併後若本 fork 決定同步整個 `docs/i18n/` 目錄，一併處理。

### 不引用：#3850 清理 workflow 裡的 flake8 指令

只改 `.github/workflows/python-app.yml`。**本 fork 沒有這支 workflow**（`ls .github/workflows/`
確認），lint 走本線自己的 CI 設定。


## 2026-08-30（補）：#3851 不引用，PR 水位 3850 → 3851

上游是 microsoft 的高速開發線，本輪處理完 `#3846`–`#3850` 之後隨即又出現 `#3851`。

**`#3851` feat: add DecisionAssure Impact – governance change impact analysis engine**：
OPEN、**100 個檔案、+8742/−434**，新增一整個「治理變更影響分析引擎」到
`agent-governance-python/agent-mesh/`。

**不引用**，兩個理由：

1. **上游還沒接受**。這是提案不是上游狀態，本 fork 的既定做法是 open PR 預設不提前引用；
   被上游合併後會經由 commit 軸抵達。
2. **本 fork 沒有現在就在痛的缺陷需要它**。這是新功能（8700 行的新引擎），不是修正。
   提前引用一個 100 檔的未採納功能，等於扛下一條上游可能不會走的分支。

**觸發條件**：上游合併它時隨 commit 軸抵達；或本線真的需要變更影響分析而上游遲遲不合併時重評。


## 2026-08-30（再補）：#3852 不引用，PR 水位 3851 → 3852

**`#3852` Loosen serde/serde_json/thiserror workspace pins**：OPEN、`+4/−4`，只動
`agent-governance-rust/Cargo.toml`，把三個依賴從精確釘版（`"=x.y.z"`）放寬成相容範圍。

**上游的理由成立，但那個理由是「發佈者」的理由**：它說對一個**發佈到 crates.io 的 library
crate** 而言，精確釘版會強迫每個下游的 `Cargo.lock` 跟著鎖死。

**本 fork 不是發佈方**：`publish.yml` 有 **9 處** `github.repository ==` guard、
`publish-containers.yml` 1 處——本 fork 的發佈流程全部被閘門擋掉，不會有任何下游消費者受這些
釘版影響。也就是說上游的痛點在這裡不存在。

**而放寬釘版對本線是負向的**：艦隊的依賴紀律是「宣告的下限是相容性承諾」，精確釘版讓本 fork
的建置可重現；放寬之後同一個 commit 在不同時間會拉到不同 patch 版，反而讓
`dependency-freshness` 的比對失去基準。

**觸發條件**：本 fork 哪天要自行發佈那些 crate（目前發佈 workflow 全被 guard 擋著）就重評；
或上游合併後隨 commit 軸抵達時，再決定要不要在本線改回精確釘版。

---

**關於這個上游的節奏**：`microsoft/agent-governance-toolkit` 是高速開發線，本輪處理
`#3846`–`#3850` 之後，`#3851`、`#3852` 在同一天內陸續出現。水位代表的是「到某個編號為止已經
逐筆看過」，不是「以後都不會再有」——之後的新項目由每週排程接手，不需要在同一輪裡追到底。
