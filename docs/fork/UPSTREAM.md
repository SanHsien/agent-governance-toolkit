# 上游維護

## Remote

- Fork：`origin` → `https://github.com/SanHsien/agent-governance-toolkit.git`（預設分支 `main`）
- 原作者：`upstream` → `https://github.com/microsoft/agent-governance-toolkit.git`（預設分支 `main`）
- 追蹤分支：`main`

## 檢查新提交

```powershell
git fetch upstream main
python tools\check_upstream_updates.py --strict
```

工具以 `tools/upstream_baseline.json` 的 `reviewed_through` 為起點，列出所有未審查提交。
有新提交或檢查失敗時，`--strict` 回傳非零；排程 workflow 也會因此明確失敗。

CI 沒有 `upstream` remote，所以 baseline 的 `repo` 寫完整 clone URL，不要寫遠端短名。

## 審查清冊

每次只做一次批次審查：

1. 讀 commit 主旨與變更檔案（open PR 必須讀 diff，禁止只憑標題結案）。
2. 判斷是否與 README overlay、Windows gate、發佈閘門或測試衝突。
3. 可直接同步的提交用 merge；只需要部分修正時 cherry-pick 或最小重做。
4. 跑 `pwsh -NoProfile -File tools\dev_check.ps1`。
5. 在 `docs/fork/DECISIONS.md` 記錄採用／略過理由。
6. 驗證完成後才把 baseline 推進到已審查的完整 40 字元 SHA。

Baseline 代表「已審查」，不代表「全部已合併」。

**四個面向都要看，不是只看 commit**：commit、open PR、open issue、上游分支。每個面向各記一個
水位（`reviewed_through`／`reviewed_pr_through`／`reviewed_issue_through`，分支記 head SHA），
下次只看更大的編號或變動過的 head。

**判準是證據，不是分類。** 結論要寫得可查證：diff 動了哪些檔案、本 fork 對應的檔案實際長什麼樣，以及**觸發條件**。

README 衝突的解法：保留頂部 fork overlay，把上游新英文內容留在 `README.md` 其餘段落。workflow 衝突時保留官方-repo-only guard。

## 2026-08-28：fork 起點

本 fork 自上游 `main` `46463ef8689433817fcc0c582a7881f515d4df15`
（`fix: enforce signed http trust verification (#3813)`）建立。此 SHA 設為第一個 `reviewed_through`。
之後的上游 commit 才需要進入審查清冊。

## 2026-08-28：上游 PR、issue、分支盤點

建立 fork 時**不引用**任何尚未進入 `main` 的 PR。本線第一個提交只加維護骨架。

當時 GitHub 上最新 issue 編號為 **#3836**，最新 PR 編號為 **#3845**。之後只看更大的編號，以及 baseline 之後的 commit。

未合併 PR 仍屬上游產品線（Claude Code 政策 preamble、spell-check 等）。要採用時必須讀完整 diff，不能只看標題。

### 分支

`gh repo clone` 會把上游 `main` 收成 `upstream/main`。本線只維護 `origin/main`。其他上游分支不追，除非審查清冊明確採用。

### 水位

- PR：已看到 **#3845**
- issue：已看到 **#3836**
- 記在 `tools/upstream_baseline.json`
