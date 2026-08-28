# CLAUDE.md

請先完整閱讀並遵守 [`FORK.md`](FORK.md)。產品規則見上游內容為主的 [`AGENTS.md`](AGENTS.md)；衝突時以 FORK.md 為準。本檔只補充 Claude Code 的最小入口。

- 這是保留上游歷史的 fork；不要移除 `upstream`、原作者或 MIT 授權標示。
- `README.md` 保持上游英文產品說明（產品測試契約）；繁中維護規則在 `FORK.md`。不要把產品 `AGENTS.md` 改寫成維護索引。
- 產品程式在 `agent-governance-python/`、各 `agent-governance-*` SDK、`policy-engine/`、`examples/`，以上游為準，除非 `FORK.md`／`REVIEW.md` 已記錄 overlay。
- 不要在本 fork 發 PyPI／npm／NuGet／GHCR，不要部署 GitHub Pages，不要把 fork-only 檔案送進上游。
- 日常修改直接推 `origin/main`，不開功能分支、不開維護 PR；需要他人審查或高風險改動才走 PR。
- 開 PR 前先 `gh repo set-default SanHsien/agent-governance-toolkit`，並明寫 `gh pr create --repo SanHsien/agent-governance-toolkit --base main --head <分支>`；建完讀輸出的 URL 確認 owner。
- 合併任何 PR（含 Dependabot）前必須讀完整 diff；CI 綠燈不等於審查過。不要自動合併。
- 提交前跑 `pwsh -NoProfile -File tools\dev_check.ps1`。產品檔有改再依 `docs/fork/DEVELOPMENT.md` 跑對應套件測試。
- API key、`.env`、Azure 憑證、稽核日誌與帳號資料一律不可提交。
- 使用繁體中文，直接交付可驗證結果，避免冗長背景鋪陳。
