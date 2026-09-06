[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory)]
        [string]$Label,
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    Write-Host "==> $Label"
    & $script:pythonExe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

Invoke-PythonStep -Label "Compile fork Python" -Arguments @(
    "-m", "compileall", "-q", "tools"
)
Invoke-PythonStep -Label "Ruff (E9 + F)" -Arguments @(
    "-m", "ruff", "check", "--select", "E9,F", "--target-version", "py310",
    "tools"
)
Invoke-PythonStep -Label "Pytest (fork tools)" -Arguments @(
    "-m", "pytest", "-c", "tools/pytest.ini", "tools/tests"
)
Invoke-PythonStep -Label "Check fork Markdown links" -Arguments @(
    "tools\check_links.py"
)

# 上游那 22 個 job 的 CI 全部鎖在 microsoft/ 名下（見 FORK.md），所以本 fork 改過的
# 產品碼在 ci.yml 裡是不會被測到的。凡是本線與上游分歧的產品檔，對應的測試要列在
# 這裡——否則它就只有本機跑過一次，之後沒有任何東西看著它。
# 目前只有 agent-os 的 MCP 認證強制這一處分歧；日後新增分歧就往下加。
Invoke-PythonStep -Label "Pytest (fork-divergent product code)" -Arguments @(
    "-m", "pytest",
    "agent-governance-python/agent-os/tests/test_mcp_auth_enforcement.py",
    "-q"
)

Write-Host "WINDOWS DEV CHECK GREEN"
