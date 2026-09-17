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

## 2026-09-12：上游 41 個提交合併、4 項關鍵 PR 採用與第二輪全量盤點

**決定**：
1. **合併 upstream/main**：將 commit 水位推進至 `0533ceaf6c5b0975bfc71bff42f6ccd2d34c8adf`（`0533cea`，`chore(deps-dev): Bump hono in /policy-engine/sdk/node (#3917)`）。合入 41 個提交，包含 Claude Code hook 啟動修復（`#3854`）、Dependabot 安全升級（`#3857`~`#3865`、`#3868`、`#3872`~`#3874`、`#3880`、`#3885`、`#3886`、`#3900`、`#3901`、`#3917`）、OpenCode 提示拒絕與秘鑰遮蔽修復（`#3674`, `#3679`）。
2. **採用 PR #3913**（`fix: opa - use --stdin-input instead of --input /dev/stdin (Windows)`）：
   - **理由**：修復 Issue #3912。Windows 沒有 `/dev/stdin`，`OPAEvaluator` CLI 模式在 Windows 執行時一律失敗並靜默回傳 `allowed=False`。改成 `--stdin-input` 移除平台相依性。本 fork 是 Windows-first，此修正屬關鍵基礎設施。
3. **採用 PR #3916**（`fix: govern - wire audit_file to FileAuditSink so file-based audit persistence actually works`）：
   - **理由**：修復 Issue #3915。`govern(audit_file=...)` 在文件上宣稱支援檔案稽核持久化，但程式碼未將參數接入 `FileAuditSink`，導致稽核日誌永遠只存在記憶體。合入其完整 HMAC 鏈式簽署、路徑正規化與檔案持久化實作。
4. **採用 PR #3924**（`fix(agent-mesh): support contains/startswith/endswith in PolicyRule condition DSL`）：
   - **理由**：條件 DSL 原先不支援字串子字串/前綴/後綴運算子，未匹配時直接 `return False`。若規則是 `deny`（例如 `action.tool startswith 'delete_'`），會被靜默放行，造成嚴重安全漏洞。此修正補齊運算子並維持 fail-closed。
5. **採用 PR #3853**（`fix(agent-os): redact secrets glued to a following suffix`）：
   - **理由**：修復 Issue #3494。當秘鑰後方緊接標註後綴（如 `_old` 或 `_rotated`）時，原有的單純 `\b` 邊界檢查無法匹配，導致真實明文秘鑰直接外洩。修正為前瞻斷言 `(?![A-Za-z0-9])`。同時在測試中加入 `ids` 參數，避開 Windows 下環境變數長度超過 32,767 字元的限制。
6. **不引用其餘 Open PR（#3853 ~ #3931 間其餘項目）**：
   - `#3856`（WebMCP 介面適配）：尚未定案之實驗性功能。
   - `#3871` / `#3931`（v5.0.1 hotfix 準備）：包含本地端開發中修改，待上游正式 release 再行評估。
   - `#3876`, `#3879`, `#3887`：內部重構與貢獻者檢查調整，本 fork 維護線不受影響。
   - `#3883`（DecisionAssure 影響分析引擎）：巨型功能提案（100+ 檔），非痛點修正，維持不提前引入政策。
   - `#3888`（Cedarling integration）：新增策略引擎整合，非現有 bug 修正。
   - `#3889`, `#3890`, `#3891`, `#3895`, `#3897`：文件/ADR/標章更新，本 fork 已有獨立文件體系。
   - 重複之 dependabot PR（如各模組的 vitest、qs、js-yaml、hono）：上游尚未完全合入，本 fork 等待上游常態依賴整併。
7. **Issue 研判（#3836 ~ #3930，共 11 項）**：
   - `#3884`：Windows CI 缺乏（本 fork 已有 Windows-first fork-maintenance 與 dev_check 覆蓋）。
   - `#3912`：OPA /dev/stdin（已由 PR #3913 解決）。
   - `#3915`：audit_file 未接入（已由 PR #3916 解決）。
   - `#3911`：BackendRegistry 與 govern 整合，已納入追蹤。
   - `#3923`：agentmesh 模組循環引用冷啟動延遲，後續追蹤。
   - `#3892`, `#3893`, `#3898`, `#3899`, `#3918`, `#3930`：RFC 與規範議題，無須程式碼操作。
8. **清理分支與 Tag/Release（落實單一最新原則）**：
   - 經使用者糾正，嚴格落實「單一最新分支、單一最新 tag、單一最新 release」。
   - 先前誤解而將上游 24 個歷史 tag 全數推至 origin，且僅以本地 git branch -r 檢查而漏掉 Dependabot 在 GitHub 上自動建立的另外 4 個分支。
   - 修正處置：將 Dependabot 4 筆安全相依性更新（PR `#3` brace-expansion、PR `#4` hono、PR `#5` @babel/core、PR `#6` js-yaml）逐一檢驗並合入 `main` 分支，隨後以 `gh api /repos/SanHsien/agent-governance-toolkit/branches` 與 `/tags` 直接查核遠端，全數刪除 4 個已合入之遠端分支與 23 個歷史舊 tags。GitHub 上僅嚴格保留單一分支 `main` 與單一最新 tag/release `v5.0.0`。
   - 規則寫入 `FORK.md` 與本檔。
## 2026-09-17：評估並合併 Dependabot PR #9（rmcp 2.0.0）與清理分支

**背景**：GitHub 針對 `rmcp < 2.0.0` 發布 2 項高風險安全通報（CVE-2026-63128 與 CVE-2026-63127），Dependabot 自動開啟 PR #9（`build(deps): bump rmcp from 1.7.0 to 2.0.0 in /policy-engine`），產生遠端分支 `dependabot/cargo/policy-engine/rmcp-2.0.0`。

**決定**：
1. **評估並合入 PR #9**：
   - **安全效益**：將 `policy-engine/Cargo.lock` 與 `policy-engine/integrations/mcp/Cargo.toml` 中 `rmcp` 由 1.7.0 升級至 2.0.0（`rmcp-macros` 至 2.2.0），修正 Unauthenticated permanent session-table leak（DoS）與 OAuth Protected Resource Metadata 未校驗問題，成功解除 Dependabot alerts #130 與 #131。
   - **相容性分析**：對照上游審計 PR #4018，此 crate 僅使用預設 feature（未啟用有漏洞之 streamable http server 或 auth 模組），且使用的 14 個符號在 2.0.0 中均無破壞性變更，編譯與測試皆綠燈。
   - **驗證**：PR #9 在 GitHub CI 之 `fork gate (ubuntu-latest)` 與 `fork gate (windows-latest)` 均通過；本地 `tools/dev_check.ps1` 亦通過。
   - **合入處置**：以 squash merge 合入 `main`，PR #9 狀態變更為 MERGED。
2. **落實單一分支原則**：
   - 合併後立即刪除 origin 上的 `dependabot/cargo/policy-engine/rmcp-2.0.0` 遠端分支。
   - 經 `git ls-remote --heads origin` 查核，遠端僅保留唯一分支 `main`。
3. **Dependabot 告警現況分析與錯誤研判**：
   - 診斷 Dependabot 更新失敗紀錄（如 Run #34697776783，針對 mastra-agentmesh 之 esbuild 更新）：因 `tsup: 8.5.1` 要求 `esbuild: ^0.27.0`，而修復版 esbuild 為 `>= 0.28.1`，npm 嘗試降級路徑失敗致使 Dependabot updater 報錯。
   - 其餘模組之 npm 告警均屬上游 checked-in lockfiles 之相依性，依照本 fork 治理原則，靜待上游常態整併（如上游 PR #4006）。
