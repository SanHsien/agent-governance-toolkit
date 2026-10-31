---
title: 維護決策
last_reviewed: 2026-10-29
owner: agt-maintainers
---

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
3. `package-lock.json` 補回 fork 已有的較新版本（不是手改，是 `npm update <pkg> --package-lock-only --ignore-scripts --legacy-peer-deps`，manifest 沒變）：`mcp-proxy`（body-parser 2.2.2→2.3.0、hono 4.13.7→4.13.13、ip-address 10.4.0→10.7.3、js-yaml 4.3.0→4.3.2、nanoid 3.3.17→3.3.20）、`mcp-server`（hono、nanoid）、`agent-governance-typescript`（@babel 系列、browserslist 系列）。`agent-hypervisor/uv.lock`：cryptography 48.0.1→49.0.0。補回並不完整：同一份 lock 的 anyio 原本有 4.14.2 與 4.15.1 兩個解析分支，合併後只剩 4.14.2（4.14.2 本身是上游 #4032 的 Dependabot 安全升版）；`@vitest/coverage-v8` 4.1.11→4.1.10、`policy-engine/Cargo.lock` 的 `rmcp-macros` 2.2.0→2.1.0（配對 `rmcp` 2.1.0，fork 先前的 CVE-2026-63127／63128 修正在 `rmcp` 2.1.0）亦為降版，未連網查證這三個版本有無獨立公告。判斷依據是把 `40efdf19` 版 lock 與上游 lock 逐套件比版本，列出「fork 較新」的清單；不是整份 lock 重新解析。
4. `agent-os/tests/test_mcp_auth_enforcement.py`：fork 原本加了四條未註冊 server 的測試，其中三條（TLS 下限、https 放行、可關閉 TLS 下限）上游已以 #3814 回歸測試收進；自動合併後兩份同名方法並存，fork 版會蓋掉上游版（ruff F811）。合併後審查發現，已刪除 fork 的三條重複，只保留上游沒有的「未給 URL 不受影響」；41 passed（上游 40）。
5. overlay：`docker-compose.yml`／OpenClaw compose 的 loopback 綁定、`requirements-dev.txt`、`.gitignore`、`docs/i18n/README.zh-TW.md` 語言列、`REVIEW.md`、`SECURITY.md`、`NOTICE.md`、`FORK.md`、`AGENTS.md` fork 段、`CLAUDE.md`、`docs/fork/**`、`tools/**`。

沒有任何一處產品原始碼（agent-mesh、agent-os、policy-engine、SDK）保留 fork 版；那些檔案與上游逐位元組相同。

**驗證證據**（隔離 venv 在 scratchpad，Windows 11、Python 3.14.8；每個測試檔各自一個行程；對照組是 `git worktree add --detach C:/GitHub/agt-upstream upstream/main`，以 `PYTHONPATH` 指向各自的 `src`）

- `git diff --name-only --diff-filter=U` 與 `git grep -nE '^(<<<<<<<|>>>>>>>) '` 皆為空。
- `pwsh -NoProfile -File tools\dev_check.ps1`：`WINDOWS DEV CHECK GREEN`（含 `tools/tests` 與 MCP 認證 41 passed）。
- agent-mesh（合併樹／純上游樹）：`test_govern` 58 passed 2 skipped／同；`test_policy_rule_string_operators` 18／18；`test_org_policy_rule_string_operators` 23／23；`test_federation` 58／58；`test_opa` 56／56（首輪存檔為 55 passed + 1 計時 flake，見下；2026-10-07 重跑 56 passed，存於 scratchpad `agt/results-merged/mesh_test_opa_rerun_20261007.txt`）（使用 OPA 0.70.0 Windows 版，SHA-256 與發行方公告一致）；`test_governance` 36／36；`governance/test_audit_backends` 34 passed 2 skipped／同；另 `test_policy_*`、`test_multi_agent_policy*`、`test_trust_policy`、`test_async_policy_evaluator`、`test_stdout_audit`、`test_govern_approval_coordinator` 全過，兩邊結果相同。`test_persistent_audit` 17 skipped（兩邊相同）。
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
- `agent-mesh/src/agentmesh/governance/audit_backends.py:33,385`：`fchmod` 僅在有此函式的平台套用。Python 3.13 起 Windows 也有 `os.fchmod`（本機 3.14.8 實測存在），所以 Windows 上會執行，但只切換唯讀旗標、不改 ACL。fork 舊版 `_append_line` 完全沒有 `fchmod`，這是上游的強化。
- `agent-mesh/src/agentmesh/governance/govern.py:86`：`audit_secret_key` 現在要求至少 32 bytes，短 key 直接 `ValueError`。
- `federation.py:1223`、`policy.py:391`：未知語法對 deny 規則 fail-closed（視為匹配）、對 allow 規則不匹配；`!=`／數值比較對缺值與非字串同樣依 action 方向 fail-closed。
- 這一輪沒有逐筆讀上游 296 個 commit 的 diff；採用依據是維護者授權整樹採用，加上上述測試與 fork-only 修正的逐項比對。

**觸發條件**：本 fork 若能建置原生 ACS SDK（需要 Rust）或有可用的 agent-os／agt-policies 完整測試環境，再把兩個套件的全套件測試補跑。

## 2026-10-09：延後 Rustls 安全修補

**決定**：延後處理 `rustls` (medium) 的 Dependabot 安全性警告。

**理由**：本機沒有 Rust toolchain，下次有 toolchain 時用 `cargo update -p rustls` 升到 0.23.45。

**觸發條件**：待具備 Rust toolchain 之後處理。重審日期：2026-11-01。

## 2026-10-10：Rustls PR45 與有限 Windows 產品驗收候選

採用 PR45 的單份 `agent-governance-rust/Cargo.lock` 候選，rustls 0.23.42 升至
0.23.45，rustls-webpki 0.103.13 升至 0.103.15。PR46 的 Copilot lock 不混入本候選。
官方產品 CI 在本 fork 被 owner guard 跳過，fork gate 也沒有原生 SDK 驗收能力。
新增本 fork 專用 Windows workflow，分別驗收 Rust、Copilot、Node 原生 SDK。

Node 僅新增 `build:test:ci`／`test:ci` 專用 script，與既有 test 相同的 bundled-dispatchers
建置及全部本機 Node 測試，補上 Cargo locked 與 TAP 報告。既有 build/test 不變。
Windows OPA 使用 repo 既有下載器的固定版本與 SHA256，兩項 OPA 測試不可 skip。
MSVC 環境跨 step 保存；不存在編譯工具或 registry 套件時必須如實失敗。

本決策記錄建立時候選尚未發布。本機無 MSVC，不宣稱 Rust／Node 原生全綠；待 root review 並更新 PR45
後取得三個 hosted Windows job 成功，才具備合併驗收證據。最終 docs／workflow／lock
必須先穩定，再跑本機 canonical fork gate 與輸入 hash；不沿用較早的 gate。

Copilot 首次乾淨 `npm ci` 揭露既有 peer 衝突，eslint-plugin 8.70.1 要求 parser
`^8.70.1`，manifest 卻固定 8.70.0。有限修補將 parser 與必要的同版本 helper 子圖
協調至 8.70.1，保留既有 plugin／TypeScript／Jest 與其他套件版本，不使用 force
或 legacy-peer-deps。handlebars 仍為 4.7.9，PR46 尚待獨立處理。

## 2026-10-11：Linux Docker sandbox 能力判定

PR45 hosted run `38123244870` 的 Rust build 成功，但 agentmesh 測試為 409 passed／
1 failed：`docker_create_session_without_docker` 把成功的 `docker info` 當成可用 Linux
sandbox，建立 `python:3.11-slim` session 失敗且原 assertion 未印出錯誤。
該 runner 為 `windows-2025-vs2026`；官方 image 安裝 Windows Docker CE。原 log 未記錄
實際 daemon `OSType`，不能把 Windows daemon 當成已觀測因果。新增唯讀診斷 step，
由後續 hosted log 提供 `docker info --format '{{.OSType}}'` 的 exit 與輸出。

此 provider 依賴 Linux image、sleep／sh 和 Linux hardening flags，因此只在 info 成功
且 UTF-8 輸出 trim 後精確為 `linux` 時可用。Windows、未知／無效回應、命令失敗均
fail closed；所有 cap-drop、no-new-privileges、read-only、network-none 與資源限制保留。
新增純判定單元測試，既有 lifecycle 測試仍執行可用 Linux 分支或不可用拒絕分支；
不 ignore／skip。Linux 分支失敗時 assertion 必須顯示實際 Err。

本輪本機不執行缺少 MSVC 的 native Cargo；canonical fork gate 不能代替 Rust 新增
測試或 Linux Docker lifecycle。驗收以最終候選 hosted Rust workspace 結果為準，且
Windows unavailable 分支成功不代表 Linux 容器實際 lifecycle 已驗證。既有 Node
125 passed／1 optional OpenTelemetry skip、兩项 OPA 實際 pass 及 Copilot 成功證據保留。

## 2026-10-11：PR46 Copilot handlebars 與 coverage YAML 依賴修補

PR46 保留 bot 的 handlebars 4.7.9→4.7.10 與 minimist dependency edge，先將 owner main
合入原 bot branch；未提交 merge 狀態由 root 完成。只修 Copilot，不包含 TypeScript、
Mastra 或 policy-engine 的其他 alerts。parser／plugin 保持 8.70.1。

Copilot 的 20 moderate audit 節點來自 coverage 開發依賴：
`@istanbuljs/load-nyc-config → js-yaml3 → argparse1 → sprintf-js`。sprintf-js 目前無
官方修補版。load-nyc-config 實際只呼叫 `yaml.load(text)`，可用 scoped override
換成保留該 API 的 js-yaml4，讓 dependency chain 改走無 sprintf-js 的 argparse2。
初始 4.1.1 候選被實際 resolver audit 揭露 high；官方 advisory 另列 repeated aliases、
merge-key chains、omap 及 empty merge sources 的 DoS，修補範圍直到 4.3.2。
因此只將這個 scoped YAML 套件固定為 4.3.2，不使用全域 override、audit fix、force
或 legacy-peer-deps，也不把安全版本下限或 dev scope 當成漏洞已修的證據。

新增 Copilot Jest 維護回歸：真實 loadNycConfig 的 mapping／sequence、YAML extends
與 cwd 正規化，以及 js-yaml CLI help／fixture parse。產品依賴測試只在 Copilot
Jest 跑，不讓 canonical fork gate 要求已安裝這些產品套件。驗收須以最終 manifests／
docs／tests 穩定後的乾淨 npm ci、build、Jest、lock 與 npm ls 無 sprintf、真實 npm audit
及 canonical gate 為準；既有 PR45 原生 Windows 證據沿用，不重跑本機 native builds。

## 2026-10-11：PR47 剩餘 TypeScript、Mastra 與 policy-engine 安全依賴

保留原 bot PR47 的 TypeScript handlebars 4.7.10 與 minimist edge，在未提交 merge
中納入 owner main 3060f55d；有效審查以該 main 為基準，既有 Copilot 修補不重做。
TypeScript coverage 的 load-nyc-config scoped override 使用已修補的 js-yaml 4.3.2，
移除 argparse1／sprintf-js 鏈；parser 由 8.70.0 最小對齊既有 plugin 8.70.1 的 peer
範圍，僅協調該 helper 子圖。新增實際 YAML mapping／sequence、extends／cwd 與 CLI
維護回歸，不升級 TypeScript／Jest 或其他產品依賴。

Mastra core 1.37.1 保持原版，僅將其 gray-matter scoped alias 指向維護中的
`npm:@11ty/gray-matter@3.0.0`。原 gray-matter4 使用 js-yaml3 的 safeLoad／safeDump，
直接套 js-yaml4 會破壞 API；維護 fork 保留 data／content，使用 yaml.load／dump，
其 js-yaml5 實際鎖定 5.4.3，改走 argparse2。移除無效的全域 sprintf-js override。
JavaScript front matter 明確拒絕且不得執行；YAML 日期維持普通字串。新增離線回歸
涵蓋 CJS／ESM、Buffer、ordinary schema、Markdown body、實際 Workspace skill loader
與 JavaScript payload 不執行；不以靜態 alias 或版本下限宣稱相容或漏洞已消除。

policy-engine 僅更新 rustls 0.23.45 與 resolver 所需的 aws-lc-rs 1.18.1、
aws-lc-sys 0.45.0、rustls-webpki 0.103.15、pkg-config 0.3.34，保留原 Windows
dependency edges；registry checksum 與 cargo metadata --locked 驗證鎖檔，不改 crypto
功能或安全 flags。本機缺 MSVC 時不做 native build，須由實際 hosted Node job 驗收。

Windows 產品 workflow 增加 owner 限定的 TypeScript／Mastra Node22 job 與路徑，
保留原三個 job、action pins、唯讀權限、credentials false、OPA 必過與 MSVC／Docker
能力修補。兩個新增 job 各 20 分鐘，具名 step timeout、乾淨 install、build、全套
Jest／Vitest（Mastra 另跑 tsc lint），並拒絕 manifest／lock mutation。不 publish。
所有最終 source／docs／workflow 穩定後才跑 focused workflow 與 canonical gate，
記錄完整輸入與 index 雜湊；兩套實際 npm audit 與 resolved graph 須逐一核對，
raw alerts 降低不是整個 repo 完成的充分證據。此決策建立時候選尚未發布；最終驗收
以 PR47 的實際 Windows jobs 與 owner main 權威安全清冊為準。

### 同候選追加：Mastra legacy provider-utils response limit backport

初版實際 audit 為 3 low，根源為 GHSA-866g-f22w-33x8：response handlers 讀取 body
沒有共同 byte cap，並非 tool approval 漏洞。官方 provider-utils 2.x 最新仍是
2.2.8；ui-utils 1.x 最新 1.2.11 仍依賴它。已修補的 3.0.28 把 safeParseJSON 改成
Promise，而該 ui-utils parsePartialJson 同步讀取 success／value，盲套 major override
會破壞 API。因此保留 core 1.37.1 與 legacy 2.2.8；v5／v6 aliases 僅升官方同 major
3.0.28／4.0.33 及必要 provider 子圖。

依官方 shared bounded reader 修補作本地 backport，僅替換 legacy CJS／ESM 的
三個 buffered JSON／JSON-error／status-error body read；safeParseJSON 與 streaming／
binary 契約不變。有限 8 MiB raw byte cap、header 提前拒絕、實際串流計量、取消與
releaseLock 清理避免無上限 body buffer；保留原 abort／read error，不以 cancel error
掩蓋。新增正常 JSON／UTF-8／error handlers、缺少／低報／無效 header、byte boundary、
oversize cancel、abort、同步 ui-utils parsePartialJson 與 hash-bound patch 回歸。

patch artifact 綁定原始與輸出 SHA256，套用程式另外綁定 artifact SHA256、版本與
固定兩個 module target；全部驗證後才寫入，未知 bytes fail closed，重入可驗證。
本 fork source checkout 使用 explicit patch／check 與 build／lint／test source pre-hook；
Windows ignore-scripts 安裝後同樣必須 explicit 套用。tarball 僅含 dist，沒有 dependency
install／postinstall hook；消費者不繼承 overrides，peer 範圍也不保證本 locked graph。
不宣稱發布套件已套 backport；source 使用者入口與限制寫在 adapter README。
不改 npm version／integrity 以偽造 audit zero，不使用 audit fix、force 或 legacy peer。

raw audit／Dependabot 對 legacy 官方版本仍可能報告 low，須保留原始 exit／nodes；
本地 runtime backport 不等於官方 alert 歸零。不變的 TypeScript 696 tests／audit0、
Cargo checksum／metadata 與原 workflow phase 保留，僅重驗變動後 Mastra 安裝／build／
lint／Vitest／audit、新 install workflow contract 與最終 canonical。所有 source／docs
先穩定，再記錄完整前後 input/index 雜湊；發布前仍須 root code 與 security review。


### 安裝契約 review 補正

移除初版 postinstall：files 僅 dist，發布 tarball 沒有本地 patch script／artifact，
且消費者不繼承 overrides 或固定 core peer graph，不能在 dependency 安裝時強制套用。
保持發布 files 契約，不把 script／patch 塞入 tarball；backport 僅適用本 fork source
checkout 的 locked 開發／驗收 graph。實際 npm pack 回歸核對 packaged manifest 無
install／postinstall 與 files 僅 dist；完整 body-limit／alias 30 tests 安全證據沿用，
只重驗變動的安裝契約、focused workflow 與最終 canonical，保留所有前期證據。


### Git checkout 位元組 binding 補正

初版本地 artifact 為 CRLF，Git 的 text/eol=lf 規則將已提交 blob 正規化為 LF，
造成 raw-byte checksum 在乾淨 checkout 不符。artifact 改用精確 LF bytes，script
固定 SHA256 為 `073ab28e26233ad22400473e0fc95341d6ff2161ab23b33fb87ae7c3d96512a1`。
JSON decoded replacements 與 provider-utils before／after hashes 不變；不放寬校驗，
不修改 Git attributes。回歸驗證 raw 與 Git clean-filter blob identity 一致，另以實際
Git blob／checkout filters 證明 LF bytes 穩定；未知 bytes 仍拒絕，patch 仍可重入。


### TypeScript Linux Docker 能力補正（2026-10-11）

PR47 Windows run 38143204918 的 TypeScript lifecycle 失敗明確顯示 daemon 使用
Windows containers，拒絕 Linux sandbox 的 read-only 選項。Docker info 成功不等於
Linux 能力可用。provider 改以固定 argv、無 shell 查詢 OSType；僅成功狀態、有效
UTF-8 且 trim 後精確 linux 才可建立 session，其餘 fail closed。保留所有 capability、
security、read-only、network 與資源限制。既有 lifecycle 在不可用環境實際斷言 session
拒絕，不以 skip 通關；純回歸涵蓋 Windows、空值、大小寫、錯誤狀態與非法 UTF-8。
本機回歸不代表 Linux Docker 真實 lifecycle 已驗證；產品驗收仍以最終 Windows
workflow 的 TypeScript job 實際結果為準，其餘已成功產品 job 證據保留。

## 2026-10-24：Dependabot 68 筆開放告警（critical 2、high 15、medium 42、low 9）一次處理

**範圍**：全部 68 筆都有修補版，沒有延後項。只動告警 `manifest_path` 對應的 manifest／lock，沒有改產品程式碼。
Code-scanning API 回 `404 no analysis found`（本 fork 沒有 CodeQL 分析結果），沒有可處理的項目。

**決定與做法**（各生態系各一個 commit，同一個 PR）：

- Rust（2 筆 medium，`rustls` GHSA-2mjx-qc3c-rqvc）：`cargo update -p rustls --precise 0.23.45`，
  只改 `policy-engine/examples/coding_agent/app/Cargo.lock`（resolver 同時把 `rustls-webpki` 0.103.13 帶到 0.103.16）
  與 `benchmarks/prompt-injection/harness/agt-rules-baseline/Cargo.lock`。`Cargo.toml` 與 `agent-governance-rust` 的
  精確釘版政策不動：本 fork 不是 crates.io 發佈方，PR45 的精確釘版決定維持。這同時結案 2026-10-09
  「延後 Rustls」那一則：當時以「沒有 toolchain」為由，現在 `~/.cargo` 有 cargo 1.98.1，`cargo update`
  與 `cargo metadata --locked` 可用；仍沒有 MSVC `link.exe`，所以不能 `cargo check`／`cargo test`。
- pip（27 筆：critical 2、high 7、medium 13、low 5）：兩個 `uv.lock` 用 `uv lock --upgrade-package <pkg>==<修補版>`
  （certifi 2026.10.19、hypervisor 另 aiohttp 3.14.4，resolver 順帶 yarl 1.25.1）。兩個 `requirements.txt`
  是人工釘版：cloud-board 的 aiohttp 3.14.4、black 26.10.1、opentelemetry-api／sdk 1.45.1 與
  instrumentation-fastapi 0.66b1（sdk 1.45.1 要求 semantic-conventions 0.66b1，三者必須一起動）；caas 的
  pypdf 6.21.1。選的都是告警列出的最小修補版（instrumentation 例外，由 sdk 約束決定）。
- npm（39 筆，6 個套件）：lock 一律由 npm 重新產生（`--package-lock-only --ignore-scripts`，不用 legacy-peer-deps、
  audit fix、force）。`@vitest/mocker` 是 `vitest` 的精確釘版子依賴，唯一的修補路徑是 vitest 4.1.11 → 4.1.12
  （mcp-server 的 `@vitest/coverage-v8` 是 vitest 的精確 peer，同步 4.1.12）。`vite` 沒有直接依賴，由 vitest
  解析到 8.3.5（在 vitest 允許的 `^8` 內，高於修補版 8.1.6）。mcp-proxy 的 `@modelcontextprotocol/sdk`
  1.31.0 → 1.32.0（精確釘版，取最小修補版）。hono 4.13.13、ip-address 10.7.4、follow-redirects 1.16.1
  是 lock-only 的 `npm update`。

**驗證**：兩個 Rust lock `cargo metadata --locked` 通過；marketplace 327 passed／2 skipped；hypervisor
69 failed／9 errors，與 origin/main 的 lock 逐項相同（既有失敗，非本次造成）；mcp-proxy、copilot 擴充、
copilot-governance、mastra 的 `npm ci`／build／test 通過（mastra 的 pack-contract 測試在本機失敗，是 Git 的
GNU tar 把 `C:` 當遠端主機，System32 的 bsdtar 解 tarball 正常，PR 的 Windows runner 才是依據）；pypdf
6.21.1 以 `PdfReader` 實測 caas 用到的 API。

**既有問題，本次不處理**：

- `agent-os/services/cloud-board/requirements.txt`：`pytest==9.0.3` 與 `pytest-asyncio==1.1.0`（要求 pytest<9）
  互相衝突，原檔就無法解析；`agent-os/services/cloud-board/requirements.lock` 與 `agent-os/modules/caas/requirements.lock`
  落後 `requirements.txt` 很多（例如 aiohttp 3.13.3），不在告警範圍。Dependabot 不讀 `*.lock`，沒有告警。
- `npm audit` 另外報了不在這 68 筆內的 `zod`（GHSA-mrhx-c7xc-m3w5，high）：mcp-proxy、mcp-server、
  mastra、policy-engine/sdk/node 都有，修補版 4.6.6 對 mastra 的 `zod 3.25.76` 是跨 major；
  待 Dependabot 開出告警或
  上游發出 3.x 修補時處理。

**觸發條件**：下一次 Dependabot 告警出現新的 `zod`／`vite`／`vitest` 項目，或 2026-11-01 重新跑
`gh api repos/SanHsien/agent-governance-toolkit/dependabot/alerts?state=open`，開放告警數應為 0（不含上述 zod）。

## 2026-10-24：上游審查第四輪（c3e8229d → 70a4ab8e）

**範圍**：128 個 commit（57 個非依賴）、195 個 PR（`--state all`：142 已合併、7 關閉未合併、46 open，其中 88 筆 Dependabot）、24 個 issue（19 open、5 closed）。水位從 commit `c3e8229d`／PR 4197／issue 4178 推進到 commit `70a4ab8e`／PR 4421／issue 4400。

**方法（結構性論證，PLAYBOOK §2 判準六）**：`git diff c3e8229d origin/main` 在產品碼上的分歧只有 mcp-server 4 個 `src/` 檔、Rust／TypeScript `sandbox*` 與少數測試；產品原始碼與上游 `c3e8229d..upstream/main` 變更檔沒有交集；交集只在非產品檔：`README.md`、11 個 workflow、`docs/i18n/README.*.md`、約 15 個 `package.json`／lock、cloud-board `requirements.txt`、`agent-hypervisor/uv.lock`、3 個 `Cargo.lock`。這些逐一處理（見下表），所以已合併的 commit 以 `git diff c3e8229d upstream/main | git apply --3way` 整批套用（fork 歷史與上游無共同祖先，改用 patch 而非橋接 merge），不逐筆重寫。

**採用（commit 軸）**：57 個非依賴 commit 扣除 TypeScript 7 遷移後的產品修正與功能（agent-sre、agent-hypervisor、agent-mesh、agent-os、agent-compliance、agent-discovery、agent-runtime、agent-sandbox、agent-lightning、agent-learning、haystack-agentmesh、a2a-protocol、dotnet、opencode、claude-code、policy-engine ACS alpha.4），包含 #4361／#4332／#4277（hypervisor denylist 繞過）、#4362（.NET 非 DID principal）、#4124（不可見字元繞過）、#4339（traceparent sampled 位元）。供應鏈 CI 腳本（#4229、#4231、#4213、#4151）一併採用。

**未採用或延後，附理由與觸發條件**：

| 項目 | 結論 | 證據與理由 | 觸發條件 |
| --- | --- | --- | --- |
| TypeScript 7 遷移（#4126、#4127） | 已於 2026-10-25 採用 | 前一輪因 jest 設定缺套件延後；本輪補齊 `@swc/jest`、`@typescript/native` 並重生 lock 後三套件 build／lint 通過、有測試的兩套件全綠，見「2026-10-25：採用 TypeScript 7 遷移」一節 | — |
| 遷移之後的 dev 依賴 PR（`@typescript-eslint`、vitest 5、`@swc/core` 升版等） | 延後 | 非安全修正；fork 維持 `@typescript-eslint` 8.70.1、vitest 4.1.12，只加遷移必要的套件 | 對應套件有安全公告，或 fork 的 Windows gate 能整組驗證時再升 |
| `README.md` 變更（ACS 說明、plugin marketplace 段落） | 不採用 | fork 的 `README.md` 是繁體中文版，衝突取 fork 側 | 維護者要同步英文說明時，改 `README.en.md` |
| 依賴衝突檔（各 `package.json`／lock／`requirements.txt`／`uv.lock`） | 取 fork 側 | fork 已套 2026-10-24 的 #48／#53 安全修補，Dependabot 會對 fork 自己開 PR | Dependabot 對應 PR |
| 三個 `Cargo.lock`（`agent-governance-rust`、`policy-engine`、`policy-engine/examples/coding_agent/app`） | 取上游側／兩側合併 | `tests/ci/test_release_tooling.py::test_acs_registry_pair_and_backend_features_are_consistent` 要求 lock 與 ACS alpha.4 一致；逐套件比對沒有任何版本倒退（rustls 0.23.45／0.23.46），只移除 `serde_yaml`、`unsafe-libyaml`、`ryu` | — |
| 已關閉未合併 #4420、#4344、#4271、#4262、#4246、#4235、#4225 | 不收 | 上游拒收或已由後續 PR 取代：#4344 已由 #4339（fork `agent-sre/.../tracing/__init__.py:108-116`）涵蓋；#4271 由 #4293／#4412 取代；#4262（移除 policy-engine）上游定調為方向但此 PR 載體不對 | #4262 方向若以新 PR 合併，會與 fork 閘門過的 `policy-engine-ci.yml`／`ci.yml` 衝突，屆時重審 |
| open 的功能／重構／CI PR：#4417、#4416（破壞性）、#4407、#4346、#4327、#4292、#4288、#4276、#4275、#4274、#4270、#4269、#4268、#4267、#4261、#4259 | 不採用 | fork 不替上游決定功能。風險：#4407 新增未加 fork 閘門的 `release-stage-label` job 並會讓 `check_no_public_preview.sh` 掃到 fork 檔而失敗；#4259 的 `--sync-registry` 會把 `policy-engine-ci.yml` 手加的閘門洗掉；#4261／#4274／#4292／#4346 若合併會帶入未閘門的 job | 上游合併後，同步時逐一補 fork 閘門 |
| 7 個 open Dependabot PR（#4398 aiohttp、#4379、#4303、#4302、#4301、#4300、#4299） | 不收 | fork 自己跑 Dependabot；aiohttp 已在 3.14.4 | — |

**採用上游尚未合併的 open PR（缺陷在 fork 現碼中實際存在，附修正位置；皆已有各套件測試通過）**：

| PR | 缺陷（fork 檔:行） | 修正 |
| --- | --- | --- |
| #4354（結案 issue #4291） | `agent-mesh/.../governance/policy.py:216-223`、`federation.py:1064-1069` 在引號內也切 `and`／`or`，deny 規則對所有請求命中、allow 永不命中 | 只在引號外切分 |
| #4356（結案 issue #4355） | `agent-hypervisor/.../session/isolation.py:76-85` 不解析 `..`，且用裸 `startswith` 無目錄邊界 | 解析路徑並檢查邊界 |
| #4409 | `agent-runtime/.../deploy.py:176-191` 呼叫端 `env` 可覆蓋 `AGT_*` 治理設定（含 kill switch） | `deploy()` 對含 `=` 的名稱，以及與 `governance_env` 的 7 個固定名稱（`AGT_POLICY_PATH`、`AGT_TRUST_LEVEL`、`AGT_AUDIT_ENABLED`、`AGT_MAX_TOOL_CALLS`、`AGT_RATE_LIMIT_RPM`、`AGT_KILL_SWITCH`、`AGT_RETENTION_DAYS`）同名的變數拒絕（`ValueError`）；其他 `AGT_*` 名稱照放行；內部呼叫端無此用法 |
| #4284 | `agent-os/.../mcp_security.py:805` 忽略設定的 `privilege_escalation` 樣式 | 使用設定 |
| #4282、#4283、#4234 | Go：`policy.go:450` 整數條件永不匹配；`identity.go:41` 壞金鑰長度 panic；`sandbox.go:266` docker exec 不吃 `TimeoutSeconds` | 補整數比較、長度檢查、逾時 |
| #4285、#4233、#4226、#4232 | `token_budget.py:105` 進度條除法應為乘法；`rate_limiter` docstring 與程式矛盾；`oci-manifest.ts:18` 不存在的 OCI v2 media type；`context-poisoning.ts:122` 寫死 `MAX_ENTRIES_PER_KEY` | 各一行級修正 |
| #4324、#4325（移植後套用） | `agent-discovery/cli/main.py:145,237` 掃描不存風險標籤與狀態；`config.py:156` Windows 反斜線使巢狀設定檔匹配失敗（Windows 專屬） | 補存檔、改用 posix 路徑；#4325 的第 3 個 hunk 與已採用的 `DOCKER_AGENT_PATTERNS` 變更衝突，已手動移植 |
| #4418 | `agent-lightning/.../reward.py:168` multiplicative 模式回報的不是實際套用的懲罰 | 回報實際值 |

這批會讓 fork 與上游短暫分歧；上游合併同一修正時，下次同步以上游版本為準。CHANGELOG 類檔案刻意不套（與 fork 的 CHANGELOG 衝突，且這些條目不屬於 fork 的變更紀錄）。

**WATCH（缺陷在 fork 存在或可能存在，暫不採用）**：

- #4411（結案 issue #4400）：補 `ExcessivePrivilegeEvaluation` 剩餘缺口（空白、list、巢狀、`admin:*`、大小寫鍵；`agent-learning/.../evaluation.py:224,236-245,563`），但語意放寬（含 `*` 的任何字串都算高權限；非字串葉節點 fail closed）。觸發：上游合併。
- #4286：`extractSqlFacets` 對 UNKNOWN 動詞回空 facets，會讓以表名為鍵的 deny 規則抓不到該類語句，需改以 `verb==UNKNOWN` 規則。觸發：上游合併並說明遷移。
- #4279：OpenCode `session.created` 移入 `event` hook（`agent-governance-opencode/lib/index.mjs:80`）；OpenCode 是否有該 hook 鍵的依據是文件，未實跑。觸發：能實跑 OpenCode 時。
- #4419：`total_reward` 變更同時改規格步驟順序（目前程式符合 AGENT-LIGHTNING-FAST-PATH-1.0 第 8 步先於第 11 步）。觸發：上游規格與程式一起合併。
- #4421／#4377（`agt-policies` 遷移器強化，互相衝突、各 +800 行）、#4376（webhook SSRF 守衛，+1791 行，預設擋內部端點；fork 的 webhook URL 來自自己的設定，不是不可信輸入）、#4320（MCP 簽章，破壞性、`CHANGES_REQUESTED`、依賴未合併的 #4132，對應 issue #4199）。觸發：上游合併其一／fork 允許不可信方設定 webhook URL。
- issue #4343（Claude Code plugin 對每個工具呼叫引數跑 `McpSecurityScanner`，`agent-governance-claude-code/lib/policy.mjs:358,497`）：fork 仍存在，無上游修正 PR；#4372（`AgentControl` 無 `close()`，`policy-engine/sdk/python/.../_orchestration.py`）、#4363（功能提案）。觸發：上游出修正 PR。
- issue #4331、#4334、#4335、#4357、#4358 已由 #4332、#4339、#4340、#4362、#4361 修掉（逐項在 fork 程式確認）；#4217、#4230、#4298、#4342、#4371、#4373、#4374、#4375、#4378、#4281、#4345、#4198 為 RFC／提案／維運，無動作。

**fork 閘門提醒**：本輪新增的兩個 job（`docs-quality.yml` 的 `owasp-badge`、`supply-chain-check.yml` 的 `cargo-source-policy`）已補 `github.repository == 'microsoft/agent-governance-toolkit'` 閘門。注意 `tools/tests/test_fork_overlay.py` 只檢查檔案內有無閘門字串，不是逐 job 檢查，不能當作閘門齊全的證據，審查才抓到缺口。同步 #4318 時 `docs/i18n/README.zh-TW.md` 的 OWASP 徽章一併改為 `7_Full,_3_Partial`（`python -I scripts/docs/check_owasp_badge.py --root .` 通過）。上游 alpha.4 刪掉了 `policy-engine/sdk/rust/Cargo.toml` 內「OPA runtime env 會讀到主機秘密」的 SECURITY 註解，風險本身未被 alpha.4 修掉，留在此處備查。上游尚未合併的 #4261／#4274／#4292／#4346 若合併，同步後要補 `github.repository == 'microsoft/agent-governance-toolkit'` 閘門。

## 2026-10-25：採用 TypeScript 7 遷移（#4126）

前一輪延後的 #4126／#4127 本輪補齊後採用。#4127 的供應鏈驗證腳本前一輪已隨整批套用在 fork；#4126 的三個套件（`agent-governance-typescript`、`agent-os/extensions/copilot`、`agent-os/extensions/mcp-server`）改用 `@typescript/native`（`npm:typescript@7.0.2`）編譯，`typescript` 別名到 `@typescript/typescript6@6.0.2` 供 lint 使用，jest 改 `@swc/jest`。

- 依賴版本保持 fork 側（`@types/node` 26.6.2、`@typescript-eslint` 8.70.1、vitest 4.1.12），只加遷移必要套件；三份 lock 以 `npm install` 重生。
- 移除 `ts-jest` 連帶移除 `handlebars`（它只是 ts-jest 的間接依賴），所以兩個 `coverage-yaml.test.ts` 的斷言從「handlebars 4.7.10」改為「lock 內無 handlebars」。
- 驗證：三套件 `build`／`lint` 通過；typescript 712 tests、copilot 17 tests 全綠；`check_lockfile_integrity`、`check_install_scripts --strict`、`check_release_age`、`check_dependency_confusion --strict` 通過；`scripts/tests`＋`tests/ci` 失敗集合（9 項）與 main 逐項相同。
- 依賴審計：`docs/dependency-audits/2026-09-24-typescript-7-toolchain.md`（取自上游）。

## 2026-10-26：補審 PR #4422–#4423、issue #4424–#4425

commit 水位不變（`70a4ab8e`，上游無新 commit）；PR 水位 4421 → 4423、issue 水位 4400 → 4425。

| 項目 | 結論 | 證據與理由 | 觸發條件 |
| --- | --- | --- | --- |
| PR #4422（agent-lightning `policy_penalty` 對 dict 違規取 severity） | 採用（移植） | fork `reward.py` 以 `getattr(violation, "severity", ...)` 讀取，dict 一律得 medium 懲罰；重現測試在舊碼失敗。只移植程式與測試，規格文件 `AGENT-LIGHTNING-FAST-PATH-1.0.md` 與 CHANGELOG 不動 | 上游合併後以上游版本為準 |
| PR #4423（ACS pre/post tool committed effects 測試） | 不採用 | 只加測試，fork 不跑 policy-engine 該套測試 | — |
| issue #4424（`run_tool` 在 `post_tool_call` 未綁定時先執行工具再拒絕） | WATCH | 行為屬 fail-closed 設計（#3528），提案是補文件並可選提早失敗；尚無修正 PR | 上游出修正 PR |
| issue #4425（8 個範例的 requirements 釘舊套件，缺 `agent_control_specification`） | WATCH | 範例相依問題，fork 不跑這些範例；尚無修正 PR | 上游出修正 PR，或 fork 要驗收這些範例時 |


## 2026-10-26（補）：上游 2 個新 commit、PR #4427、issue #4426

commit 水位 `70a4ab8e` → `46b370e7`（上游 `6dc2093e`、`46b370e7`）；PR 水位 4423 → 4427、issue 水位 4425 → 4426。PR #4427 依 PLAYBOOK 判準八取目前 head `bc596b0410d6a3d21978c7a82c70a16724d37e98`（單一 commit，359 行 diff）掃描：無長空白夾帶內容、無超過 300 字元的行、無 `eval`／`exec`／`subprocess`／長 base64 或 hex；唯一的 `base64` 是測試用的簽章編碼。

| 項目 | 結論 | 證據與理由 | 觸發條件 |
| --- | --- | --- | --- |
| commit `6dc2093e`（#4418，agent-lightning multiplicative 模式回報實際懲罰） | 已存在，補規格文件 | 程式與測試 2026-10-24 以 open PR 形式採用：`reward.py` 與 `tests/test_lightning_comprehensive.py` 和上游 `main` 逐位元組相同（`git diff HEAD upstream/main -- <file>` 該測試檔為空；`reward.py` 唯一差異是本 fork 領先的 #4422 dict severity，見上一節）。fork 缺的只有規格文件段落：`docs/specs/AGENT-LIGHTNING-FAST-PATH-1.0.md` 第 6.5 節仍寫舊的「penalty 一律取自 severity 表」，與已採用的程式矛盾，本輪從上游 `main` 取該檔（上游與 fork 的差異就只有這個 commit 的 11 行／5 行，無 fork 分歧）。CHANGELOG 條目照慣例不套 | — |
| commit `46b370e7`（#4259，`generate_workflows.py --sync-registry`） | 不採用 | 上一輪就預判過它的風險，本輪實測：(1) fork 的 `generate_workflows.py --check` 在現況已紅（`policy-engine-ci.yml (out of date, run --write)`），原因是 fork 手加了 `github.repository == 'microsoft/agent-governance-toolkit'` 閘門，生成器不知道；`--sync-registry` 結尾會呼叫 `--write` 路徑，會把這些閘門洗掉。(2) 上游 `tests/ci/test_generate_workflows.py` 新增的 4 個符號連結測試（`test_sync_registry_refuses_symlinked_registry_path`、`test_intra_repo_symlinked_composite_file_is_rejected`、`test_symlinked_composite_actions_dir_is_rejected`、`test_composite_action_symlink_escape_is_rejected`）在本機 Windows 用 `Path.symlink_to` 直接拋 `OSError: [WinError 1314]`（沒有建立符號連結的權限），也沒有 `skipif`；套用後 `pytest tests/ci/test_generate_workflows.py` 由 2 failed／14 passed 變成 6 failed／30 passed。(3) 該工具是 opt-in，fork 的 `ci-generation-check.yml` 已被 `github.repository` 閘門擋掉，fork 不跑它。 | 把 fork 閘門做進 `.github/ci/workflows.toml` 清單、讓 `--check` 在 fork 轉綠；或上游讓符號連結測試在無權限時 `skip`。屆時整批取上游版本 |
| PR #4427（`agentmesh-integrations/parmana-trust-verify`，新增第三方 Parmana trust-record 驗證整合；7 檔 +317） | 不採用 | 新增整合套件，不是缺陷修正；依賴 PyPI 上的外部套件 `parmana-verifier`，會進 fork 的依賴新鮮度與供應鏈閘門，而 fork 沒有任何使用 Parmana 的呼叫端（`git grep -il parmana` 除本節外無命中）。fork 不替上游決定新增哪些第三方整合；首次貢獻者、尚無 review | 上游合併，且 fork 有實際要驗證 Parmana 記錄的使用者 |
| issue #4426（RFC：ApprovalResolution 的 detached Ed25519 簽章，ADR-0030 選用延伸） | WATCH | RFC，沒有缺陷、沒有修正 PR；提案預設關閉、不動 hash chain，金鑰管理明列為範圍外 | 上游出實作 PR；屆時看 Python 與 .NET 的簽章欄位是否一致 |

## 2026-10-28：上游審查第五輪（46b370e7 → 9bfdd5f4）

**範圍**：37 個 commit、40 個 PR（#4428–#4467，`--state all`：34 已合併、5 open、1 已關閉未合併）、0 個新 issue（上游最新 issue 仍是 #4426）。水位：commit `46b370e7` → `9bfdd5f4`、PR 4427 → 4467、issue 4426 不變。

**方法**：先量分歧（PLAYBOOK §2 判準六）。`git diff --stat upstream/main HEAD -- <產品目錄>` 仍有 79 個檔案分歧（上一輪採用的 open PR 修正、TypeScript 7 遷移、依賴鎖檔），所以不能用結構性論證，逐筆處理：37 個 commit 中 33 個是 Dependabot 依賴升版（PR #4429–#4466），4 個是產品修正（#4409、#4419、#4422 是水位之前的 PR，#4460 在範圍內）；40 個 PR 中 34 個已合併（33 個依賴升版加 #4460）、3 個是 open 的 Dependabot PR（#4431、#4453、#4467），其餘 3 個（#4428、#4461、#4464）逐筆讀 diff。三個仍開著或被關閉的 PR 依判準八取目前 head 並掃描：#4428 `919e9262`、#4461 `d10a479e`、#4464 `6159f330`，另掃三個 open 的 Dependabot PR（#4431 `1b35880a`、#4453 `249181b6`、#4467 `a2ece0cb`），皆無長空白夾帶內容、無 `eval`／`new Function(`／`globalThis`、無長 base64／hex；超過 300 字元的行都是 CHANGELOG 條目。

### 採用

| 項目 | 結論 | 證據 | 重看條件 |
| --- | --- | --- | --- |
| commit `e490800`（#4460，agent-sre 實驗流量依相對權重分配） | 採用（取上游版本） | fork `experiments/__init__.py:143,146` 用 `random.random()` 對未正規化的權重累加：三個預設權重 0.5 的變體，第三個永遠拿不到流量。上游新增的 4 個流量測試在舊碼 3 個失敗，換上游實作後 21 個全過（連跑 3 次） | — |
| commit `9bfdd5f`（#4419，`GovernedEnvironment.total_reward` 含成功獎勵） | 採用（取上游版本，含規格文件） | fork `environment.py:306` 在加入 `success_bonus`（`:325`）之前就累計 `total_reward`，回合總報酬少算每個乾淨步驟的 10.0。上一輪 WATCH 的觸發條件是「上游規格與程式一起合併」，這次一起合了：`docs/specs/AGENT-LIGHTNING-FAST-PATH-1.0.md` 與程式都取上游，fork 在這些檔上的分歧只剩上一輪的 #4422 註解。新測試在舊碼失敗，agent-lightning 全套 211 passed／1 skipped | — |
| commit `c3f0555`（#4422，`policy_penalty` 對 dict 違規取 severity） | 已存在，補註解與上游測試 | 2026-10-26 已移植邏輯；這次取上游 `reward.py`（差異只有 docstring 與註解）與 `test_lightning_comprehensive.py` 的 3 個測試。fork 自己的 `tests/test_policy_penalty_dict.py` 保留（重複但無害） | — |
| commit `fcc8eb1`（#4409，DockerDeployer 的 `env` 不得覆蓋治理設定） | 已存在 | 2026-10-24 以 open PR 形式採用；`git diff HEAD upstream/main -- deploy.py tests/test_deploy.py` 為空，逐位元組相同 | — |
| PR #4461（agent-sre GitOps `RolloutSpec.to_dict()` 寫 CRD 欄位名；open，上游作者被要求再 rebase） | 採用上游尚未合併的 open PR（移植程式與測試，CHANGELOG 不動；`.cspell-repo-terms.txt` 補 `gitops`） | fork `gitops.py:95-96` 寫 `duration_seconds`／`manual_gate`／`comparator`，而 reconciler `k8s/__init__.py:328-340` 讀 `durationSeconds`／`manualGate`／`operator`，所以 GitOps 規格經 reconciler 讀回來時步驟間隔變預設 3600、人工閘門消失、回滾運算子變 `gte`。PR 的 2 個新測試在 fork 現碼失敗，套用後 agent-sre 全套 1413 passed，失敗與錯誤集合與套用前逐項相同（皆為本機缺 otel／langfuse／openlit 套件）。上游合併同一修正時以上游版本為準 | 上游合併或改寫此修正 |

### 不採用或 WATCH

| 項目 | 結論 | 證據與理由 | 重看條件 |
| --- | --- | --- | --- |
| PR #4428（`AgentControl.run_tool` 在 `post_tool_call` 未綁定時先拒絕、不執行工具；對應 issue #4424；open，Ricky-G 已 approve） | WATCH（adoption pending，本機無法驗證） | 缺陷在 fork 存在：`policy-engine/sdk/python/agent_control_specification/_orchestration.py:301-363` 與上游逐位元組相同，`run_tool` 先執行工具、再收到 `post_tool_call` 的拒絕。PR 改 `_orchestration.py`（+90）、`_types.py`、3 份文件、1 個 308 行測試。這個 SDK 的測試要先建出 Rust 原生擴充 `_native`（`pytest tests/test_orchestration.py` 在 collection 即 `ImportError: cannot import name '_native'`），本機沒有 `cargo`／`maturin`，無法在採用前跑測試；fork 目前也沒有任何呼叫端依賴這條路徑 | 上游合併；或本機／CI 能建出 `_native` 再移植 |
| PR #4464（`AgentControl.close()` 與 context manager；對應 issue #4372） | 不收 | 已關閉未合併，作者 MaryamIjazMaryam 自己關閉，PR 本文是未填的範本；是新增 API 而不是修正，測試同樣需要 `_native`。issue #4372 維持 WATCH | 上游出合併的修正 PR |
| PR #4431（Rust `serde-saphyr` 1.2.0 → 2.0.0，open） | 不採用 | 主版本升級，改 `Cargo.toml`／`Cargo.lock`（+32/-5）；fork 在 `agent-governance-rust/Cargo.toml:29` 精確釘 `=1.2.0`，主機沒有 `cargo` 無法建置驗證。fork 自己跑 Dependabot | fork 的 Dependabot 對應 PR，且 Windows gate 能建置 |
| PR #4453（pypdf 6.19.0 → 6.21.2，open） | 已存在 | fork `agent-os/modules/caas/requirements.txt:4` 已是 `pypdf==6.21.2` | — |
| PR #4467（agent-hypervisor `certifi` 2026.5.20 → 2026.10.18，open） | 不採用 | 該 PR 的目標版本比 fork 低：fork `agent-hypervisor/uv.lock:348` 已是 `2026.10.19`，PR 是 225/189 行的整份 lock 重生 | — |
| 33 個已合併 Dependabot commit／PR（#4429、#4430、#4432–#4452、#4454–#4459、#4462、#4463、#4465、#4466） | 不收 | 沿用前幾輪的結論：fork 自己跑 Dependabot，鎖檔衝突取 fork 側。逐項比對 fork 現況：已持有的有 setuptools 84.1.0（`requirements/ci-build.txt:4`、`agent-learning/pyproject.toml:2`）、`fast-uri` 3.1.9（mcp-server、mcp-proxy、mastra 三份 lock）、`body-parser` 2.4.0／1.20.9（copilot、mcp-server、mcp-proxy、api 的 lock）、`zod` 4.6.7（mcp-proxy）、certifi 2026.10.19。落後的只有：Rust `cedar-policy`（`Cargo.toml:18`，`=4.13.0` → 4.14.0）、`regorus`（`:26`，`=0.12.0` → 0.13.0），這兩個是精確釘版的 minor 升級，沒有 `cargo` 無法建置；`gh-action-pypi-publish` 1.14.2（`publish.yml:350,444`，該 workflow 閘在官方 repo，fork 不跑）；.NET `Microsoft.Agents.AI` 1.22.0、`Microsoft.Extensions.DependencyInjection` 10.0.12、`Microsoft.NET.Test.Sdk` 18.10.1、`Microsoft.SourceLink.GitHub` 10.0.401；mcp-server 的 `zod` 4.6.6；Python 開發工具的宣告下限（`fastapi>=0.143.0`、`hypothesis>=6.169.0`、`opentelemetry-sdk>=1.44.0`、`setuptools>=84.0.0`）。後者是相容性承諾，不為了追新而調高（PLAYBOOK §1）。以上只比對 fork 現況與上游目標版本，本輪沒有逐項查安全公告，所以不主張這些落後是安全無關 | 對應套件有安全公告，或 fork 的 Dependabot 開出 PR |

### 順帶記錄

- `agent-governance-python/agent-sre` 全套測試在本機有 18 failed／11 errors，來源是缺 `opentelemetry`、`langfuse`、`langsmith`、`openlit` 套件（採用前後集合逐項相同），不是本輪改動造成。
- `tools\dev_check.ps1` 的「fork-divergent product code」只列 `test_mcp_auth_enforcement.py`；上一輪與本輪採用的 open PR 修正（#4354、#4356、#4461 等）的測試沒有列入。這是既有缺口，需要先決定 agent-sre 等套件的測試依賴怎麼在 Windows gate 安裝，列為需維護者決定的事。

## 2026-10-28：Dependabot 15 筆新告警（rustls 8、qs 4、deepmerge 2、dnspython 1）

**成因**：不是 `6e3b703a`、`40800add` 造成。這兩個提交只動 `.github/workflows/fork-product-windows.yml`、`FORK.md`、`docs/fork/DEVELOPMENT.md`、`tools/tests/`，沒有碰任何 manifest 或 lock。告警來自新發佈的公告：dnspython GHSA-45c3-73f7-pv4m（2026-10-27 15:37Z，high）、rustls 四則 GHSA-h2v8-394m-p7vv／c8m5-c952-6cm4／w44r-93j7-qv28／vp88-798v-h67f（16:08Z 前後，low×3、medium×1）、qs GHSA-6pq8-jhm2-2vcw（16:10Z，medium）；GitHub 在 2026-10-28 07:03Z 一次建立。deepmerge GHSA-gcqx-w48m-w2h4 公告是 2026-09-18，同一批建立。10-24 清掉的 68 筆當時沒有這些公告，所以「開放告警歸零」的前提是公告不再新增。

**做法**（依 2026-10-24 的慣例：fork 自己改告警 `manifest_path` 對應的 lock，選最小修補版）：

- rustls 0.23.45 → 0.23.46（`cargo update -p rustls --precise 0.23.46`）：`agent-governance-rust/Cargo.lock`、`policy-engine/Cargo.lock`，各只改 rustls 的 version 與 checksum 兩行，`Cargo.toml` 不動。`policy-engine/examples/coding_agent/app/Cargo.lock` 已是 0.23.46。`benchmarks/prompt-injection/harness/agt-rules-baseline/Cargo.lock` 仍是 0.23.45：沒有告警，而且該 lock 落後 `Cargo.toml`，`cargo update -p rustls` 會連帶改 56 行（thiserror、移除 unsafe-libyaml 等），超出告警範圍，所以還原不動。
- qs 6.16.0／6.15.2 → 6.16.1：copilot 擴充與 `agent-mesh/services/api` 原本就有精確釘版 override（`"qs": "6.16.0"`），改成 `"6.16.1"`；mastra-agentmesh 與 `policy-engine/sdk/node` 沒有 override，依同一慣例新增 `"qs": "6.16.1"`。不用 `npm update`，因為它會挑 6.17.0（2026-10-27 才發佈，不到 7 天冷卻期）。lock 由 `npm install --package-lock-only --ignore-scripts` 重生；`policy-engine/sdk/node` 連帶 `side-channel` 1.1.0 → 1.1.1（qs 6.16.1 的依賴要求）。
- dnspython 2.8.0 → 2.9.0：`agent-hypervisor/uv.lock` **只手術式替換 dnspython 一個區塊**（版本、sdist、wheel 的 URL 與 sha256，與 PyPI JSON 逐項相符）。原因：此 lock 自 `2c18a903` 之後就落後於 `pyproject.toml` 的 dev 下限（fastapi、hypothesis、mypy、pydantic、ruff、uvicorn），`uv lock --upgrade-package dnspython==2.9.0` 會把整份 lock 重生（841 行，ruff 0.16→0.17、pydantic-core 2.46→2.50 等）。重生區塊取自該指令的輸出，其餘不動；`pyproject.toml` 沒有改，也沒有提高任何宣告下限。2.9.0 需要 Python ≥3.11，與 `requires-python = ">=3.11"` 相符。

**驗證**：

- Rust：兩個 lock `cargo metadata --locked` 通過；`agent-governance-rust` `cargo test --locked` 414＋24＋13＋6＋1 全過（Windows MSVC 工具鏈現在可用，`cargo check` 也通過）；`policy-engine` `cargo test --locked --workspace --no-fail-fast` 144 passed／5 failed，與還原原 lock 後的基準逐項相同（5 個都是 `*zero_config*`／`real_*` 測試；本機 PATH 沒有 `opa`，推測與此有關，未逐一驗證原因，重點是前後集合相同）。
- npm：五個 lock 都 `npm ci --ignore-scripts` 乾淨；copilot build＋Jest 17 passed；mastra patch 檢查、build、`tsc --noEmit`、vitest 31 passed（`pack-contract` 在 Git 的 GNU tar 下失敗，是 2026-10-24 已記的環境問題，PATH 前置 System32 的 bsdtar 後通過）；`services/api` build＋測試 11 passed。`policy-engine/sdk/node` 只驗 `npm ci` 與 `npm ls qs`，沒有跑 `build:test`（需要 napi 原生建置與固定 OPA），qs 只經 `@modelcontextprotocol/sdk` 的 express 進入。
- Python：hypervisor 在 dnspython 2.8.0 與 2.9.0 下 `pytest tests` 都是 90 failed／571 passed／9 errors，集合相同，是既有失敗（乾淨 venv 缺鎖定版本）。

**延後：deepmerge（2 筆，GHSA-gcqx-w48m-w2h4，low）**：`agent-governance-typescript/package-lock.json` 與 `agent-os/extensions/copilot/package-lock.json`。影響版本 4.2.0–4.3.1，`npm view deepmerge versions` 最新就是 4.3.1，**沒有修補版**。scope 是 development，唯一路徑是 `jest` → `@jest/core` → `jest-config` → `deepmerge@4.3.1`，只在測試時執行，不進發佈物。不用 override 換成別的套件（deepmerge 的 API 會被 jest-config 直接呼叫，換掉等於 fork jest）。告警維持 open，不 dismiss。**重看條件**：①npm 出現 deepmerge > 4.3.1；②`jest-config` 升版後不再依賴 deepmerge（`npm ls deepmerge` 為空）；③Dependabot 對這兩筆列出 `first_patched_version`；④任何一個路徑變成 runtime（非 development）依賴。

**既有問題，本次不處理**：`agent-hypervisor/uv.lock` 與 `pyproject.toml` 的 dev 下限不同步（見上），下次因告警必須重生 lock 時一併處理，並單獨審視 mypy／ruff／pydantic 的跳版。

## 2026-10-29：deepmerge 延後項目重查

**範圍**：在 `ef6ee043688861922d852bc972b18ef852b1c5e2` 工作樹重新查核前節延後裁決；查詢時間為 2026-10-29（Asia/Taipei）。本次只更新維護文件，不修補產品行為。

**修補訊號**：

- `gh api 'repos/SanHsien/agent-governance-toolkit/dependabot/alerts?state=open' --paginate` 成功（exit 0）。全部開放告警仍只有 #292（`agent-governance-typescript/package-lock.json`）與 #286（`agent-governance-python/agent-os/extensions/copilot/package-lock.json`）；兩筆皆為 `GHSA-gcqx-w48m-w2h4`、low、development、transitive，`first_patched_version: null`，影響範圍 `>= 4.2.0, <= 4.3.1`。
- `npm view deepmerge versions --json` 成功（exit 0），結尾為 `4.3.0`、`4.3.1`，沒有更高版本。[GitHub 公告](https://github.com/advisories/GHSA-gcqx-w48m-w2h4) 同樣顯示 Patched versions 為 None；公告最後更新為 2026-10-27。

**依賴用途**（Node `v26.12.1`、npm `11.20.0`）：

- 兩套件起初尚未安裝依賴，`npm ls deepmerge` 都顯示 `(empty)` 並 exit 1；不能據此判定依賴已移除。
- 分別執行 `npm ci --ignore-scripts --no-audit --no-fund --prefix agent-governance-typescript` 與 `npm ci --ignore-scripts --no-audit --no-fund --prefix agent-governance-python/agent-os/extensions/copilot`，皆 exit 0，分別安裝 400 與 522 個套件；manifest 與 lock 未變更。
- 分別執行 `npm ls deepmerge --prefix agent-governance-typescript` 與 `npm ls deepmerge --prefix agent-governance-python/agent-os/extensions/copilot`，皆 exit 0，只有以下開發依賴路徑：

```text
jest@30.4.2 -> @jest/core@30.4.2 -> jest-config@30.4.2 -> deepmerge@4.3.1
```

- 同兩個指令加上 `--omit=dev` 後皆為 `(empty)`、exit 1（npm 表示沒有匹配套件，並非安裝失敗）；正式執行依賴不含 deepmerge。兩套件的 `src/` 也未找到 deepmerge 引用。

**裁決**：原有四項重看條件皆未成立，繼續延後；兩筆告警保留 open，不 dismiss、不替換 API、不重生 lock。已完成的是本次重查，並非漏洞已修復。後續仍依前節四項條件重看，不另立待辦清單。

## 2026-10-30：policy Python SDK 原生擴充（_native）Windows 建置能力盤點

**背景與範圍**：
路線圖「盤點 Windows gate 是否能建出 policy Python SDK 原生擴充」旨在確認本機／Windows 環境是否能建出 `policy-engine/sdk/python` 的 Rust 原生擴充 `_native`，為後續採用 PR #4428（`AgentControl.run_tool` 在 `post_tool_call` 未綁定時提前拒絕）提供驗收前提（對應 issue #4424、PR #4428；前次記錄見 2026-10-28 第 703 行）。盤點範圍限於 SDK 原生擴充建置與 `tests/test_orchestration.py` 驗收，不包含 PR #4428 的代碼移植，不宣稱已採用修正。

**前置依賴盤點**：

1. **MSVC C/C++ 工具鏈**：
   - 需安裝 Visual Studio 2022 C++ Build Tools（本機 `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`，MSVC v14.44）。
   - 建置時需載入 DevShell（`Common7\Tools\Microsoft.VisualStudio.DevShell.dll`），確認 `cl.exe` 與 `link.exe` 可用。
   - 需指定 `CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER` 指向 MSVC x64 linker，避免使用非 MSVC linker。
2. **Rust 工具鏈**：
   - 本機已安裝 cargo 1.98.1、rustc 1.98.1（`x86_64-pc-windows-msvc`），位於 `~/.cargo/bin`。
   - 執行建置前須將 `~/.cargo/bin` 置於 `PATH`。
3. **Python 與建置工具**：
   - Python ≥ 3.11（實測 Python 3.14，patch 版本推定，見下）。
   - 依 `pyproject.toml` 要求安裝 `maturin==1.8.7`、`pyyaml>=6.0`。
   - 關鍵注意事項：`maturin` 在 PEP 517 build hook 內部透過 subprocess 呼叫 `maturin` CLI，因此虛擬環境的 `Scripts` 目錄必須包含在 `PATH` 中，否則會報 `FileNotFoundError: [WinError 2]`。

**建置與驗證過程**：

1. 建立乾淨隔離環境於系統臨時目錄（`$env:TEMP\agt_policy_sdk_env`，事後該目錄已不存在），安裝 `maturin==1.8.7`、`pytest`、`pyyaml`。
   - 推定 base Python 為 `C:\Python314\python.exe`（現為 3.14.10；建置 PATH 含此目錄、測試 pyc 為 cpython-314；venv 已刪，無法回證確切 patch 版本）；建 venv 的確切指令當時未記錄，一般形式為 `C:\Python314\python.exe -m venv $env:TEMP\agt_policy_sdk_env`。
   - VS 安裝路徑以 `vswhere -all -products '*' -property installationPath` 查得 `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`；進 DevShell 的形式為 `Import-Module "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\Microsoft.VisualStudio.DevShell.dll"; Enter-VsDevShell -VsInstallPath "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools" -DevCmdArguments '-arch=x64'`（路徑已驗證存在，當時實際輸入的字串未記錄）。
   - 同機存在的 linker：`C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\link.exe`，`CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER` 應指向它；當時實際設定值未記錄。
   - 建置時 PATH 前段（取自 `policy-engine/target/release/build/ring-*/output`）：cargo 自加的 target 與 rustup 路徑之後，依序為 `%TEMP%\agt_policy_sdk_env\Scripts`、`%USERPROFILE%\.cargo\bin`、MSVC 14.44.35207 `bin\HostX64\x64`，之後是 VS 工具路徑；`C:\Python314` 在其後。
   - 現存產物佐證：`policy-engine/target/wheels/agent_control_specification-0.4.0b0-cp311-abi3-win_amd64.whl`、`policy-engine/target/maturin/_native.dll`。
2. 在 `policy-engine` 根目錄執行：
   `pip install --no-build-isolation ./sdk/python`
   成功建置出 ABI3 wheel：`agent_control_specification-0.4.0b0-cp311-abi3-win_amd64.whl`（3.85 MB），並成功安裝至隔離環境。git 追蹤檔案無變動；建置產物 `policy-engine/target/` 與測試快取留在 .gitignore 範圍內。
3. 匯入驗證：
   `python -c "import agent_control_specification._native as _native; print(_native.NativeRuntime)"`
   成功匯入 `_native.pyd`，確認 `NativeRuntime` 類別正常載入，未出現 `ImportError: cannot import name '_native'`。
4. 測試驗收：
   在 `policy-engine/sdk/python` 執行 `pytest tests/test_orchestration.py -v`：
   12 passed in 0.21s，全數通過。
5. 完整測試套件前置依賴補充盤點：
   執行 `pytest tests -q --tb=short`（全套 347 測試）：
   299 passed、42 skipped、6 failed。
   失敗的 6 筆全數集中於 `tests/test_validation.py`，原因為系統 `PATH` 缺少 `opa.exe`（錯誤訊息為 `OPA validation failed: program not found`），與既有 Rust policy-engine 狀態一致。`test_orchestration.py` 本身不依賴 OPA，可獨立全數通過。

**裁決**：
- 實機確認 Windows 環境具備建置 policy Python SDK 原生擴充 `_native` 並通過 `test_orchestration.py` 的完整能力。
- 解除 PR #4428（run_tool 提前拒絕修正）原先「本機無法驗證 _native」之封鎖條件，待後續任務進一步執行 PR #4428 的採用與驗證。本盤點不宣稱已採用該修正。

## 2026-10-31：採用 PR #4428（run_tool 提前拒絕修正）

**背景與範圍**：
對應 issue #4424、上游 PR #4428（`AgentControl.run_tool` 在 `post_tool_call` 未綁定時先拒絕、不執行工具；open，Ricky-G 已 approve）。在未修復前，`AgentControl.run_tool`（以及 `protect_tool` 與 MCP、LangChain 等 adapter）在 manifest 未綁定 `post_tool_call` 時，會先執行工具 callable 產生副作用，隨後才因未綁定干預點拋出 `AgentControlBlocked`（`runtime_error:intervention_point_unknown`），導致外部呼叫端收到阻擋錯誤但工具已實際被執行，且重試可能導致副作用重複發生。前次盤點（2026-10-30）已解除建置封鎖，本次任務進行移植、驗證與採用。

**缺陷重現與驗證**：

1. **缺陷重現**：
   - 先將 PR #4428 的新測試檔案 `policy-engine/sdk/python/tests/test_run_tool_unbound_post.py` 移植至工作樹，在未修改 `_orchestration.py` 的現碼上執行 `pytest`。
   - 實測結果：13 項測試中 4 項失敗（`AssertionError: Lists differ: [{'amount': 100}] != [] : the tool ran although the call was reported blocked`、`AssertionError: 1 != 0`、`AssertionError: Lists differ: [{'amount': 5}] != []`、`AssertionError: AgentControlBlocked not raised`）。確認在未修復前，未綁定 `post_tool_call` 時工具確實被執行且佔用 slot，缺陷在 Windows 環境確實重現。
2. **移植修正**：
   - 移植 PR #4428（commit `919e9262`）的實作與文件：
     - `policy-engine/sdk/python/agent_control_specification/_orchestration.py`：在 enforce 模式下，`run_tool` 於 pre-check 通過後先檢查 manifest 是否綁定 `post_tool_call`（支援 `extends` 繼承鏈），若未綁定則在呼叫工具前直接拋出 `AgentControlBlocked(InterventionPoint.POST_TOOL_CALL, ...)` 並釋放 tool call 預留 slot。
     - `policy-engine/sdk/python/agent_control_specification/_types.py`：更新 `AgentControlBlocked` 文件註解，說明 `run_tool` 在未綁定 `post_tool_call` 時提前拒絕的例外行為。
     - 文件同步：`docs/tutorials/55-agent-control-specification.md`、`policy-engine/QUICKSTART.md`、`policy-engine/README.md`、`policy-engine/sdk/python/README.md`。
3. **驗證結果**：
   - `pytest tests/test_run_tool_unbound_post.py -v`：13 passed in 0.46s，全數通過。證明未綁定 `post_tool_call` 時工具 callable 不被調用（`tool.calls == []`）。
   - `pytest tests/test_orchestration.py -v`：12 passed in 0.26s，既有編排測試全數維持通過。
   - `pytest tests -q --tb=short`（全套 360 測試）：312 passed、42 skipped、6 failed（6 failed 均為缺少外部 `opa.exe` 依賴，與 2026-10-30 基準完全一致）。
   - 本機閘門 `pwsh -NoProfile -File tools\dev_check.ps1`：全數綠燈（exit 0）。

**裁決**：
- 採用上游 PR #4428（commit `919e9262` head）之修正、測試與文件更新。
- 路線圖「近期：可以直接動手」表格中相應項目完成並移除。
- 上游 CHANGELOG 條目照慣例不套。
- 這是與上游分歧的產品碼：上游合併或改寫此修正時，以上游版本為準。
- 測試需要 `_native`；`tools/dev_check.ps1` 不裝產品套件，`fork-product-windows.yml` 也沒有 policy Python SDK job，所以目前只有本機跑過，沒有 CI 守著（路線圖中期已列）。
