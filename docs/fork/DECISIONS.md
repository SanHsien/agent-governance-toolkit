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

## 2026-09-17：評估並合併 Dependabot PR #9~#27 與清理分支

**背景**：GitHub 針對相依性漏洞自動觸發 Dependabot 安全更新，陸續產生 PR #9~#27：
- PR #9：`rmcp` 2.0.0 in `/policy-engine`
- PR #10：`js-yaml` 3.15.2 in `/agent-governance-typescript`
- PR #11：`vitest` 4.1.11 in `mastra-agentmesh`
- PR #12：`vitest` 4.1.11 in `copilot-governance`
- PR #13：`vitest` 4.1.11 in `agent-os/extensions/mcp-server`
- PR #14：`hono` 4.13.8 in `agent-os/extensions/mcp-server`
- PR #15：`fast-uri` 3.1.8 in `agent-os/extensions/mcp-server`
- PR #16：`qs` 6.16.0 in `agent-os/extensions/mcp-server`
- PR #17：`js-yaml` 3.15.2 in `agent-os/extensions/copilot`
- PR #18：`@hono/node-server` 2.1.1 in `agent-os/extensions/mcp-server`
- PR #19：`brace-expansion` in `agent-os/extensions/copilot`
- PR #20：`js-yaml` 4.3.2 in `mcp-proxy`
- PR #21：`hono` 4.13.8 in `mcp-proxy`
- PR #22：`vitest` 4.1.11 in `mcp-proxy`
- PR #23：`rmcp` 2.1.0 in `/policy-engine`
- PR #24：`fast-uri` 3.1.8 in `mcp-proxy`
- PR #25：`@hono/node-server` 2.1.1 in `mcp-proxy`
- PR #26：`body-parser` 2.3.0 in `mcp-proxy`
- PR #27：`qs` 6.16.0 in `mcp-proxy`

**決定**：
1. **評估並合入 PR #9~#27**：
   - **PR #9 & #23 (`rmcp` 2.0.0 -> 2.1.0)**：徹底解決 `policy-engine` 兩項高風險 CVE（CVE-2026-63128 與 CVE-2026-63127），對照上游審計 PR #4018，引用符號完全相容，編譯測試全綠。
   - **PR #10, #17, #20 (`js-yaml`)**：解決 `agent-governance-typescript`、`copilot` 擴充套件與 `mcp-proxy` 內部之 `js-yaml` 多項 DoS 與 CPU 耗盡漏洞。
   - **PR #11~#13, #22 (`vitest` 4.1.11)**：解決 `mastra-agentmesh`、`copilot-governance`、`mcp-server` 與 `mcp-proxy` 之 `@vitest/mocker` 路徑走訪任意檔案讀取漏洞。
   - **PR #14~#16, #18, #21, #24~#27**：解決 `mcp-server` 與 `mcp-proxy` 之 `hono`、`fast-uri`、`qs`、`body-parser` 與 `@hono/node-server` 漏洞。
   - **PR #19**：解決 `copilot` 擴充套件內部之 `brace-expansion` 記憶體消耗 DoS 漏洞。
   - **驗證**：所有 PR 均通過 GitHub Actions 之 `fork gate (ubuntu-latest)` 與 `fork gate (windows-latest)`；本地 `tools/dev_check.ps1` 全綠。
   - **合入處置**：依序以 squash merge 合入 `main`，19 筆 PR 均正常結案為 MERGED，已修復告警數由 30 增加至 97（成功解決 67 項漏洞告警）。
2. **嚴格落實單一分支原則**：
   - 各 PR 合入後立即以 `--delete-branch` 刪除 origin 上的遠端分支。
   - 經 `git ls-remote --heads origin` 查核，遠端嚴格僅保留唯一分支 `main`。
3. **Dependabot 告警現況分析與錯誤研判**：
   - 診斷 Dependabot 更新失敗紀錄（如 Run #34697776783，針對 mastra-agentmesh 之 esbuild 更新）：因 `tsup: 8.5.1` 要求 `esbuild: ^0.27.0`，而修復版 esbuild 為 `>= 0.28.1`，npm 嘗試降級路徑失敗致使 Dependabot updater 報錯。
   - 其餘 19 個模組之 npm/uv 告警均屬上游 checked-in lockfiles 之相依性，依照本 fork 治理原則，靜待上游常態整併（如上游 PR #4006）。

## 2026-09-19：落實繁體中文為主、保留中英雙語 README 與作業系統純 Windows 支援

**決定**：
1. **語系文件收斂（僅保留繁體中文與英文，以繁體中文為主）**：
   - 根目錄 `README.md` 改為以繁體中文為主的產品說明與導覽，置頂提供語系切換器至 `README.en.md`。
   - 根目錄建立英文規格與產品文件 `README.en.md`，置頂提供語系切換器至 `README.md`。
   - 清理移除 `docs/i18n/` 下所有非繁體中文、非英文文件（刪除 `README.ja.md`、`README.ko.md`、`README.zh-CN.md`、`quickstart.ja.md`、`quickstart.ko.md`、`quickstart.zh-CN.md`），僅保留 `README.zh-TW.md`、`quickstart.zh-TW.md` 與英文 `README.md`。
   - 同步更新 `mkdocs.yml` 與相關導覽切換器，僅保留 English 與 繁體中文。
2. **作業系統純 Windows 支援**：
   - 於 `README.md`、`README.en.md`、`FORK.md`、`CLAUDE.md` 明確標示本 fork 僅支援 Windows 作業系統（Windows 11 / Windows Server），以 PowerShell 為主要開發與驗收環境。
   - `.github/workflows/fork-maintenance.yml` 移除 `ubuntu-latest` 執行環境矩陣，收斂為純 `windows-latest` 執行 `tools/dev_check.ps1`，移除非必要之跨平台冗餘。
3. **驗證與單一分支**：
   - 更新 `tools/tests/test_fork_overlay.py`，驗證中英雙語 README 架構與必要檔案存在。
   - 本地 `tools/dev_check.ps1` 驗收全綠（WINDOWS DEV CHECK GREEN）。
   - 推送至 `origin main`，遠端嚴格維持單一分支。

## 2026-09-30：第三輪上游審查（275 commit／222 PR／38 issue）

範圍：commit `0533cea`..`9f2512f`、PR `#3932`–`#4197`、issue `#3931`–`#4178`。本線與上游無共同祖先，只能 `cherry-pick -x`；本機 gate 不安裝產品依賴，產品套件測試多數無法在本機執行。

**採用**（cherry-pick，測試已在本機通過）：

- `#4157`（`6b64456` → `119656e`）：`mute_agent` scrubber 處理 dict key、tuple 子類別不再崩潰。diff 2 檔 43 行；`agent-os/tests/test_mute_agent.py` 21 passed。

**採用待辦（adoption pending）**，觸發條件＝本 fork 具備可執行對應套件測試的環境（`pip install` 各套件）後逐一重評：

- 安全／fail-closed 修正，本機無法驗證：`#4070`（email/basic auth 掃描複雜度）、`#4131`（MCP replay nonce 原子性）、`#4132`、`#4123`、`#4124`（編碼／不可見字元規避）、`#4069`／`#4130`／`#3746`（agt-policies；缺 `agent_control_specification`，cherry-pick 已試、測試無法 import）、`#4071`、`#4066`、`#4096`／`#4135`／`#4138`／`#4140`／`#4147`／`#4148`（agent-mesh 稽核一致性）、`#3953`、`#4026`、`#4029`、`#4158`／`#4105`／`#3955`／`#3934`（redactor；與已採用的 `#3853` 有相依，`8be4268` cherry-pick 於測試檔衝突）。
- `#4160`（agent-sre 指標反向）：cherry-pick 乾淨，但 `agent_sre` 無法 import，已捨棄。
- `#4192`／`#4193`／`#4194`／`#4152`、`#4161`／`#4162`、`#4107`：agent-mesh／agent-sre，本機無法驗證。
- OpenCode／Claude Code plugin：`#4129`／`#4142`／`#4167`／`#4179`／`#4175`／`#4178`（issue）；Node 套件測試不在本 gate。

**不適用／跟隨上游**：

- policy-engine ACS 重構與衍生修正（`#3939`、`#3940`、`#4004`、`#4014`–`#4059` 系列、issue `#3941`–`#3948`、`#4005`、`#4042`、`#4043`、`#4047`）：Rust／PyO3 大型重構，本線不建置該套件；跟隨上游。
- 新功能：`#4063` Codex hooks、`#4065`、`#4101`、`#4099`、`#4100`、`#4102`、`#4164`、`#4168`、`#4045`、`#4052`、Studio（`#4170`、`#4195`、`#4155`、`#4169`）、healthcare（`#4153`、`#4154`、`#4156`）：新增能力，非缺陷修正。
- Windows 相關：`#3913` 已在第二輪採用；本輪無新增 Windows 專屬項目。
- 依賴升級（約 120 commit／PR：npm、pip requirement、NuGet、cargo、GitHub Actions）：Dependabot 已於本線獨立處理，不逐筆合入。
- CI／workflow（`#3950`、`#3951`、`#3887`、`#4006`、`#4033`、`#4038`、`#4103`、`#4151`、`#4196`、`#4127`）：本線 workflow 全部鎖官方 repo。
- 文件／ADOPTERS／ADR／i18n（含西班牙文 README `#3673`）／CODEOWNERS：本線僅保留繁中與英文；其餘為上游專屬。
- TypeScript 7、rust `ed25519-dalek`／`serde-saphyr` 升級（`#4126`、`#4104`、`#4008`）：大型升版，本機無法建置驗證。
- 其餘 issue（`#3933`、`#3952`、`#3954`、`#3957`、`#4012`、`#4019`、`#4048`、`#4061`、`#4062`、`#4095`、`#4106`、`#4134`、`#4137`、`#4139`、`#4141`、`#4146`、`#4165`、`#4172`、`#4174`）：對應上述 PR 的問題描述，隨對應 PR 一併處置。

水位：commit `9f2512f3c70fc907fa7ddb41caea19aba046af84`，PR `4197`，issue `4178`。Baseline 代表已審查，不代表已合併。


## 2026-10-06：全樹採用上游 `c3e8229d`（296 commit，一次性整樹同步）

**決定**：維護者授權採用上游全部待辦工作。把上游 `main` `c3e8229dfb19c697468cfb790495d7174ef8bc45`（`c3e8229d`，`chore(deps): Bump fast-uri (#4223)`）整樹併入本 fork，baseline 由 `9f2512f` 推進到此 SHA。範圍：`0533cea`..`c3e8229d` 共 296 個 commit。2026-09-30 記為 adoption pending 的安全修正（`#4070`、`#4131`、`#4132`、`#4123`、`#4124`、agent-mesh 稽核一致性、redactor `#4158`／`#4105`／`#3955`／`#3934` 等）隨整樹一起進來，不再逐筆 cherry-pick。

**方法**：本 fork 的歷史在 2026-09-28 被 squash，與上游沒有共同祖先，所以用橋接 commit 製造可合併的祖先：

1. `git merge -s ours --allow-unrelated-histories 0533cea`（橋接 commit，樹不變；`0533cea` 是上次合併的上游點）。
2. `git merge upstream/main`，三方合併的 base 即 `0533cea`；30 個檔案衝突，逐檔解決。
3. 最終分支 `sync/upstream-c3e8229d` 只有一個新 commit，父為本 fork 當時的 `main`（`40efdf19`），樹等於上面解決後的合併結果。上游 296 個 commit 不進本 fork 的歷史，與 2026-09-28 squash 的方針一致。

**解決原則**：產品碼（agent-mesh、agent-os、policy-engine、SDK）以上游為準；fork 這邊只有「上游後來改寫過的 cherry-pick」就取上游，fork 專屬修正才疊在上游之上。overlay 檔保留 fork 版，只併入上游的事實性更新。

**衝突表（30 個）**

| 檔案 | 解決 | 理由 |
| --- | --- | --- |
| `agent-mesh/.../governance/audit_backends.py` | 上游 | fork 版是 `#3916` 的早期版本；上游改為「resume 時驗證整條鏈、略過不可解析行」，更嚴格 |
| `agent-mesh/.../governance/federation.py` | 上游 | 上游的 `OrgPolicyRule` 運算子實作涵蓋 fork 版全部運算子，另加錨定、缺值、NaN／inf、未知語法 fail-closed |
| `agent-mesh/.../governance/govern.py` | 上游 | 上游已有 `audit_secret_key`／`AGT_AUDIT_SECRET_KEY`，且加了 32 byte 下限 |
| `agent-mesh/.../governance/opa.py` | 上游 | `#3913`（`--stdin-input`）已在上游，並抽出 `_rego_file_for_cli()` |
| `agent-mesh/.../governance/policy.py` | 上游 | 同 federation；`contains`／`startswith`／`endswith`（`#3924`）上游版為超集 |
| `agent-mesh/tests/test_govern.py` | 上游 | 測上游行為；fork 版 `audit_secret_key=b"irrelevant-for-reading"` 在新 resume 驗證下不再成立 |
| `agent-mesh/tests/test_policy_rule_string_operators.py` | 上游 | 上游為超集；fork 的 `test_empty_operand_does_not_match_every_string` 測的行為已被上游改成 fail-closed 的「畸形條件」，被上游新測試取代 |
| `agent-mesh/tests/test_org_policy_rule_string_operators.py` | 上游 | 同上 |
| `agent-os/src/agent_os/credential_redactor.py` | 上游 | 上游版涵蓋 `#3853` 的全部 pattern，並修正 Google API key 結尾 `-` 與 Basic auth 掃描複雜度 |
| `agent-os/src/agent_os/mcp_auth_enforcement.py` | 上游 | `#3849` 已在上游；fork 只剩註解差異 |
| `agent-os/tests/test_credential_redactor.py` | 逐 hunk：保留 fork 的 `ids=`，其餘上游 | 見下「保留的 fork 差異」 |
| `agentmesh-integrations/copilot-governance/package.json` | fork | 保留 `overrides.esbuild ^0.28.1`，見下 |
| `agent-os/extensions/mcp-server/package.json` | 上游 | 上游版本都不低於 fork 版；`@vitest/coverage-v8` 4.1.10 是上游自己的組合 |
| `agent-governance-typescript/package.json` | 上游 | `js-yaml` 5.4.2、`@noble/*` 較新 |
| `policy-engine/integrations/mcp/Cargo.toml` | 上游 | `rmcp = "2.1.0"`（含 CVE 修正），與 `Cargo.lock` 一致 |
| `policy-engine/Cargo.lock` | 上游 | 與上游 manifest 一致 |
| `policy-engine/core/tests/opa.rs` | 接受上游刪除 | 上游已移除該 dispatcher；`with_eval_timeout` 在上游 `policy-engine` 全無，`#3848` 的修正對象已不存在 |
| `.github/workflows/auto-merge-dependabot.yml` | 接受上游刪除 | 本 fork 不自動合併（`AGENTS.md`：合併前讀每個 PR diff）；fork 版只是加了官方 repo 閘門的同一支 workflow，不是測試必需的 no-op。`tools/tests/test_fork_overlay.py` 改為鎖「它不存在」 |
| `agent-governance-{antigravity-cli,claude-code,copilot-cli,opencode}/package-lock.json`（4） | 上游 | 上游版 `js-yaml 4.3.2` 已含 fork 的修正 |
| `agent-mesh/packages/mcp-proxy/package-lock.json` | 上游 + `npm update` | 見下 |
| `agent-os/extensions/mcp-server/package-lock.json` | 上游 + `npm update` | 見下 |
| `agent-governance-typescript/package-lock.json` | 上游 + `npm update` | 見下 |
| `agent-hypervisor/uv.lock` | 上游 + `uv lock --upgrade-package cryptography` | 見下 |
| `README.md` | fork | 繁中主頁保留；併入上游事實更新（OWASP 徽章改為「7 項完整、3 項部分」，並把繁中頁「10/10 覆蓋」「13,000+ 測試」的主張同步更正） |
| `mkdocs.yml` | 上游 + 移除語系 | 語言切換器只留 English 與繁體中文（移除上游新增的 Español 與既有的 日本語／한국어／简体中文）；以位元組為準保留上游的 CRLF，避免整檔空白差異 |
| `docs/i18n/README.md` | fork | 語系表只列 English 與繁體中文 |
| `docs/i18n/README.ko.md` | 維持刪除 | fork 只留 zh-TW 與英文 |

解決類型計數：上游整檔 10、逐 hunk 或保留 fork 3、manifest／lock 取上游 12（其中 4 個再以 `npm update`／`uv lock` 補回 fork 已有的安全版本）、fork overlay 2、接受刪除 3。

**非衝突檔的後續處置**

- `docs/i18n/README.es.md`、`quickstart.es.md`：上游新增，fork 只留 zh-TW 與英文，移除。
- `agent-mesh/tests/governance/test_audit_backends.py`：自動合併後出現重複的 `TestFileAuditSinkConstructionValidation`／`TestFileAuditSinkExternalRotation`（fork 的 `#3916` 舊副本與上游新版並存），其中舊版 `test_write_after_external_replace_resyncs_to_new_file` 在新驗證下失敗。改取上游整檔（同時去掉 `email_validator` 的 MagicMock shim，完整安裝依賴後不需要）。
- 新 workflow `redteam-benchmark.yml`（無 secret、不發佈，但是 `ubuntu-latest` 的上游 CI）：加 `github.repository == 'microsoft/agent-governance-toolkit'` 閘門。`ci.yml` 新增的 `engine-api-conformance`、`terraform-examples` 兩個 job 靠 `needs: changes` 間接被閘，補上顯式閘門以與其他 job 一致。逐 job 檢查全部 workflow：除 `fork-maintenance.yml`、`upstream-check.yml`、`dependency-freshness.yml` 外都有閘門（直接或經 `needs`）。
- `README.en.md`（鏡像上游英文 README）：併入 OWASP 徽章、Codex CLI 列、k8s-agent-sandbox 範例列。
- `REVIEW.md`、`tools/tests/test_fork_overlay.py`、`tools/dev_check.ps1` 註解：隨 `auto-merge-dependabot.yml` 刪除與產品碼分歧消失而更新。

**保留的 fork 差異（疊在上游之上）**

1. `agent-os/tests/test_credential_redactor.py`：`@pytest.mark.parametrize(..., ids=["akia", "ghp", "aiza", "sk_live"])`。pytest 會把 parametrize id 放進環境變數 `PYTEST_CURRENT_TEST`；10 萬字元的 id 超過 Windows 環境變數 32,767 字元上限。證據：純上游樹跑 `test_credential_redactor.py` 是 153 passed、8 errors；合併後 157 passed。
2. `agentmesh-integrations/copilot-governance/package.json`：`overrides.esbuild ^0.28.1`，lock 為 esbuild 0.28.2（上游為 0.27.7，低於 Dependabot 告警的修正版 0.28.1）。同樣的 `mastra-agentmesh` override、`agent-os/extensions/copilot` 的 `qs 6.16.0` override、`agent-mesh/services/api` 的 `qs 6.16.0`、`examples/reasoning-attestation-governed` 的 `cryptography==50.0.1` 本來就是 fork-only 且上游沒有動，自動合併保留。
3. `package-lock.json` 補回 fork 已有的較新版本（不是手改，是 `npm update <pkg> --package-lock-only --ignore-scripts --legacy-peer-deps`，manifest 沒變）：`mcp-proxy`（body-parser 2.2.2→2.3.0、hono 4.13.7→4.13.13、ip-address 10.4.0→10.7.3、js-yaml 4.3.0→4.3.2、nanoid 3.3.17→3.3.20）、`mcp-server`（hono、nanoid）、`agent-governance-typescript`（@babel 系列、browserslist 系列）。`agent-hypervisor/uv.lock`：cryptography 48.0.1→49.0.0。判斷依據是把 `40efdf19` 版 lock 與上游 lock 逐套件比版本，列出「fork 較新」的清單；不是整份 lock 重新解析。
4. `agent-os/tests/test_mcp_auth_enforcement.py`：fork 的兩條測試（未註冊 server 的 TLS 下限、未給 URL 不受影響），上游沒有，自動合併保留；41 passed（上游 40）。
5. overlay：`docker-compose.yml`／OpenClaw compose 的 loopback 綁定、`requirements-dev.txt`、`.gitignore`、`docs/i18n/README.zh-TW.md` 語言列、`REVIEW.md`、`SECURITY.md`、`NOTICE.md`、`FORK.md`、`AGENTS.md` fork 段、`CLAUDE.md`、`docs/fork/**`、`tools/**`。

沒有任何一處產品原始碼（agent-mesh、agent-os、policy-engine、SDK）保留 fork 版；那些檔案與上游逐位元組相同。

**驗證證據**（隔離 venv 在 scratchpad，Windows 11、Python 3.14.8；每個測試檔各自一個行程；對照組是 `git worktree add --detach C:/GitHub/agt-upstream upstream/main`，以 `PYTHONPATH` 指向各自的 `src`）

- `git diff --name-only --diff-filter=U` 與 `git grep -nE '^(<<<<<<<|>>>>>>>) '` 皆為空。
- `pwsh -NoProfile -File tools\dev_check.ps1`：`WINDOWS DEV CHECK GREEN`（含 `tools/tests` 與 MCP 認證 41 passed）。
- agent-mesh（合併樹／純上游樹）：`test_govern` 58 passed 2 skipped／同；`test_policy_rule_string_operators` 18／18；`test_org_policy_rule_string_operators` 23／23；`test_federation` 58／58；`test_opa` 56／56（使用 OPA 0.70.0 Windows 版，SHA-256 與發行方公告一致）；`test_governance` 36／36；`governance/test_audit_backends` 34 passed 2 skipped／同；另 `test_policy_*`、`test_multi_agent_policy*`、`test_trust_policy`、`test_async_policy_evaluator`、`test_stdout_audit`、`test_govern_approval_coordinator` 全過，兩邊結果相同。`test_persistent_audit` 17 skipped（兩邊相同）。
- agent-os：`test_credential_redactor` 157 passed（上游樹 153 passed + 8 errors，原因見上）；`test_mcp_auth_enforcement` 41（上游 40）；`test_mute_agent` 21／21。
- `npm install --package-lock-only --ignore-scripts` 在 scratch 複本：13 個動過的 npm 套件 manifest 皆可解析，lock 一致（五個 CLI 套件只差 lock 根部一段 npm 11 不寫的 `overrides`，是上游 lock 本來就有的）。`uv lock --check`：`agent-hypervisor`、`agent-marketplace` 通過。Cargo：14 個 `Cargo.toml` 與 `Cargo.lock` 可被 TOML 解析，`policy-engine` 整個目錄與上游相同。

**未能驗證**

- 本機沒有 cargo／maturin，原生 ACS SDK（`policy-engine/sdk/python`）未建置；`agent-governance-toolkit-core` 依賴的 `agent-control-specification>=0.4.0b0` 不在 PyPI，因此用 `uv pip install --no-deps -e` 裝同層套件並手動裝 `dev` extra 的依賴。依賴 ACS 原生執行期的測試（agt-policies、agent-os 的 ACS 路徑）未跑。
- 所有 Rust 測試（含 `policy-engine`）、所有 npm 套件的 `vitest`／`tsc`／build、.NET、Go 皆未跑。
- 只跑了衝突與相關模組的測試檔，不是兩個套件的全套件；上游 CI 全部鎖在官方 repo，本 fork 沒有其他自動化會跑它們。
- `test_opa.py::TestBuiltinEvaluator::test_evaluation_timing`（`evaluation_ms < 100`）在機器忙碌時偶發失敗（133.9ms），重跑三次 2 過 1 敗，屬計時 flake，與合併無關（該檔與上游相同）。
- `@vitest/coverage-v8` 4.1.10 搭 `vitest` 4.1.11、`@typescript-eslint/eslint-plugin` 8.70.1 搭 `parser` 8.70.0（peer 要求 ^8.70.1）是上游 `mcp-server` manifest 自己的狀態；嚴格 peer 解析會 ERESOLVE，需 `--legacy-peer-deps`。`agent-governance-typescript` 同樣需要。未修，因為那是上游 manifest。
- `policy-engine/Cargo.lock` 取上游後，fork 之前的 `rmcp-macros 2.2.0` 回到 2.1.0（與 `rmcp 2.1.0` 配對）；沒有 cargo，無法重新解析。

**安全相關、需要審查者特別看的上游 hunk**

- `agent-os/src/agent_os/credential_redactor.py:178`：Basic auth 的 URL 內嵌憑證 pattern 由 fork 的 `(?<![A-Za-z0-9])[a-z][a-z0-9+.-]*://` 變成上游的 `[a-z0-9+.-]{1,64}://`（無左邊界、scheme 長度上限 64）。上游註解說這是為了避免無 `://` 的分隔符密集輸入造成重複掃描，且長 scheme 仍 fail-closed 遮蔽。命中範圍比 fork 版更寬，不會變弱；但行為與 fork 版不是逐字相同。
- `agent-mesh/src/agentmesh/governance/audit_backends.py:429`（`_read_last_hash`）：fork 版對「結尾壞行」寬容；上游版改成對整條既有鏈做簽章驗證，鏈不符時 `FileAuditSink` 建構就 `ValueError`（fail-closed），不可解析的行改在 `_iter_parsed_entries`（約 222 行）略過。更嚴格，但是行為變更：用不同 key 開同一檔會直接失敗。
- `agent-mesh/src/agentmesh/governance/audit_backends.py:33,385`：`fchmod` 僅在有此函式的平台套用；Windows 上既有檔案的權限不會被收緊（上游註解已說明 Windows 無對應概念）。
- `agent-mesh/src/agentmesh/governance/govern.py:86`：`audit_secret_key` 現在要求至少 32 bytes，短 key 直接 `ValueError`。
- `federation.py:1223`、`policy.py:391`：未知語法對 deny 規則 fail-closed（視為匹配）、對 allow 規則不匹配；`!=`／數值比較對缺值與非字串同樣依 action 方向 fail-closed。
- 這一輪沒有逐筆讀上游 296 個 commit 的 diff；採用依據是維護者授權整樹採用，加上上述測試與 fork-only 修正的逐項比對。

**觸發條件**：本 fork 若能建置原生 ACS SDK（需要 Rust）或有可用的 agent-os／agt-policies 完整測試環境，再把兩個套件的全套件測試補跑。
