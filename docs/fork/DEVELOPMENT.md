# 開發環境

維護者與 AI 接手用的開發文件。產品使用方式在 [`README.md`](../../README.md)；上游同步在 [`UPSTREAM.md`](UPSTREAM.md)；決策在 [`DECISIONS.md`](DECISIONS.md)；風險快照在 [`../../REVIEW.md`](../../REVIEW.md)。

## 架構

```text
Agent / Framework（LangChain、CrewAI、MAF、OpenAI Agents …）
        │
        ▼
 govern() / Kernel adapter     攔截 tool call、委派、API
        │
        ├── Policy engine      YAML / OPA / Cedar / ACS（policy-engine/）
        ├── Identity           SPIFFE / DID / mTLS
        └── Audit log          SHA-256 / Merkle 稽核
        │
        ├── Allowed ──► Tool 執行
        └── Denied  ──► GovernanceDenied
```

Python 產品在 `agent-governance-python/`。TypeScript、.NET、Rust、Go SDK 在對應的 `agent-governance-*` 目錄。`examples/` 是可跑的整合範例。根目錄 `tools/`、`docs/fork/`、`FORK.md` 是本 fork 的開發與治理骨架，不要當成產品裝包。

## 本機開發（Windows）

### 維護骨架（必跑）

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PYTHONUTF8 = "1"
pwsh -NoProfile -File tools\dev_check.ps1
```

等價一鍵：

```powershell
pwsh -NoProfile -File tools\bootstrap_dev.ps1
```

沒有實際跑過 Windows gate，不要宣稱本機開發環境已可用。這個 gate **不安裝** `agent-governance-toolkit[full]`，因此 **不能** 證明 LangChain／CrewAI 治理路徑在這台 Windows 上已可攔截 tool call。

### 產品使用（可選，不進 fork CI）

官方套件仍從上游發佈：

```powershell
pip install "agent-governance-toolkit[full]"
```

從原始碼開發單一 Python 套件時，以上游 [`CONTRIBUTING.md`](../../CONTRIBUTING.md) 的步驟為準（需 Python 3.10+；本機 gate 用 3.14 只跑維護工具）。

```powershell
cd agent-governance-python
python -m venv .venv
.venv\Scripts\activate
pip install --no-cache-dir --no-deps -e agent-governance-toolkit-core
pip install -e "agent-os[dev]"
cd agent-os
pytest
```

不要把完整 monorepo 測試矩陣當成 fork 一鍵驗收。官方 TypeScript／.NET／Rust／Go 矩陣保留上游 repo 閘門；本 fork 的有限 Windows 產品驗收另由下列 workflow 執行。

可選 dashboard（本線 overlay 只聽本機）：

```powershell
docker compose --profile dashboard up --build dashboard
```

瀏覽器開 <http://127.0.0.1:8501>。埠綁在 loopback；容器內 Streamlit 仍聽 `0.0.0.0`，那是給 Docker mapping 用。

## Canonical gate

`tools\dev_check.ps1` 會依序：

1. `python -m compileall`（`tools`）
2. `ruff check`（E9 + F，target py310）
3. `pytest -c tools/pytest.ini tools/tests`
4. `python tools/check_links.py`
5. `pytest agent-governance-python/agent-os/tests/test_mcp_auth_enforcement.py -q`

`fork-maintenance.yml` 僅在 Windows 跑同一套。推 `main` 前先跑本機 gate。

## 有限 Windows 產品驗收

`fork-product-windows.yml` 僅在本 fork 的相關產品路徑 push／PR 與手動觸發時執行。
七個獨立 job 分別驗收 Rust workspace、Copilot extension、原生 policy Node SDK、
TypeScript SDK、Mastra adapter、agent-sre 與 agent-lightning。
官方生成的 `policy-engine-ci.yml` 與發布 guard 保持原狀。

- Rust 執行 `cargo build --release --workspace --locked` 與
  `cargo test --release --workspace --locked`。
- Copilot 執行 `npm ci --ignore-scripts`、`npm run build`、`npm test -- --runInBand`。
- TypeScript SDK 執行 `npm ci --ignore-scripts`、`npm run build`、`npm test -- --runInBand`。
- Mastra adapter 執行 `npm ci --ignore-scripts`、`npm run patch:dependencies` 與
  `node scripts/patch-provider-utils.mjs --check`，再執行 `npm run build`、
  `npm run lint` 與 `npm test`。安裝 hook 被關閉時，backport 不會自動套用；
  explicit patch／verify 不可省略。完整契約見 Mastra adapter 的 README。
  兩者使用 Node 22，job cap 為 20 分鐘；維護回歸放在各自產品套件，
  不讓 fork gate 要求已安裝產品依賴。驗收後以 git diff 拒絕 manifest／lock 變動。
- agent-sre 與 agent-lightning 各跑整套 `python -m pytest tests`（Python 3.13，job cap 20 分鐘），
  不使用 `--deselect` 或 marker 過濾；新的失敗不得靠排除測試來變綠。
  agent-sre 的 `pip install -e ".[dev]"` 會解析 `agent-governance-toolkit-core`，其釘住的
  `agent-control-specification` 預發行版不在 PyPI（上游要另外建原生 SDK），pip 會退回已發佈的 4.x
  wheel。因此 job 以內嵌 Python（`tomllib`）讀 `pyproject.toml` 的 `dev` extra 安裝，
  另補 `httpx`、`cryptography`（否則 API server 與 SBOM 簽章測試會 skip），並以
  `PYTHONPATH=src` 直接匯入原始碼。agent-lightning 無執行期相依，直接 `pip install -e ".[dev]"`；
  其 `test_backward_compat_shim` 需要 `agent_os`（optional extra），會以 `importorskip` 跳過。
- Node SDK 執行 `npm ci --ignore-scripts`、checksum 固定的 Windows OPA 下載與
  `npm run test:ci`。專用 `build:test:ci`／`test:ci` 保留既有 `npm test` 的建置與測試操作，
  另透過 napi 的 `--cargo-flags="--locked"` 傳至 Cargo，僅建置一次。
  既有 `build`／`build:test`／`test` 不變。
  TAP 中兩項 bundled OPA 測試必須實際通過，skip 會讓 job 失敗。

Rust／Node job overall cap 為 60 分鐘，build／test step 有各自具名上限。
本機若沒有 MSVC，不重跑原生建置；本機 fork gate 不能取代上述 hosted 結果。
原生產品驗收必須取得該提交的 hosted Windows 實證；本機 fork gate 不能作為替代。

## 不要做的事

- 不要把 `README.md` 改寫成維護索引。
- 不要在本 fork 發 PyPI、npm、NuGet 或 GHCR。
- 不要部署 GitHub Pages 文件站。
- 不要拿真實 Azure 租戶、生產稽核日誌或未公開政策包當 fixture。
- 不要啟用 Dependabot 自動合併。
- 不要把 dashboard／OpenClaw demo 埠改回對 `0.0.0.0` 發佈，除非維護者明確要對區網開放。
