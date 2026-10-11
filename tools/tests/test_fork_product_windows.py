from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def workflow() -> dict:
    # BaseLoader keeps YAML's `on` key a string instead of a YAML 1.1 boolean.
    return yaml.load(
        (ROOT / ".github/workflows/fork-product-windows.yml").read_text(),
        Loader=yaml.BaseLoader,
    )


def test_windows_product_scope_and_permissions() -> None:
    doc = workflow()
    assert doc["permissions"] == {"contents": "read"}
    assert doc["on"]["push"]["branches"] == ["main"]
    assert doc["on"]["pull_request"]["branches"] == ["main"]
    assert doc["on"]["push"]["paths"] == doc["on"]["pull_request"]["paths"]
    assert "workflow_dispatch" in doc["on"]
    assert "agent-governance-rust/**" in doc["on"]["push"]["paths"]
    assert "policy-engine/**" in doc["on"]["push"]["paths"]
    assert "agent-governance-python/agent-os/extensions/copilot/**" in doc["on"]["push"]["paths"]
    assert set(doc["jobs"]) == {"rust", "copilot", "node"}
    for job in doc["jobs"].values():
        assert job["if"] == "github.repository == 'SanHsien/agent-governance-toolkit'"
        assert job["runs-on"] == "windows-latest"
        assert 0 < int(job["timeout-minutes"]) <= 60
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", step["uses"])
                if step["uses"].startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] == "false"


def test_locked_native_build_and_required_opa_results() -> None:
    doc = workflow()
    rust = "\n".join(s.get("run", "") for s in doc["jobs"]["rust"]["steps"])
    assert "cargo build --release --workspace --locked" in rust
    assert "cargo test --release --workspace --locked" in rust
    node = "\n".join(s.get("run", "") for s in doc["jobs"]["node"]["steps"])
    assert "scripts/fetch-opa.mjs --platform win32-x64" in node
    assert "npm run test:ci 2>&1" in node
    assert "Required OPA test did not pass without skip" in node
    assert "(?m)^ok \\d+ - " in node
    assert "zero-config fromPath builds with bundled defaults" in node
    assert "zero-config fromPath uses bundled opa with an empty PATH" in node
    package = json.loads((ROOT / "policy-engine/sdk/node/package.json").read_text())
    locked = package["scripts"]["build:test:ci"]
    assert '--cargo-flags="--locked"' in locked
    assert "--features bundled-dispatchers" in locked
    assert package["scripts"]["test:ci"] == "npm run build:test:ci && node --test --test-reporter=tap test/*.test.mjs"
    assert package["scripts"]["test"] == "npm run build:test && node --test test/*.test.mjs"
    expected_build = package["scripts"]["build:test"].replace(
        "--dts native.d.ts", '--dts native.d.ts --cargo-flags="--locked"'
    )
    assert locked == expected_build
    for job in (doc["jobs"]["rust"], doc["jobs"]["node"]):
        setup = next(s["run"] for s in job["steps"] if s.get("name") == "Enable installed MSVC tools")
        assert "$env:GITHUB_ENV" in setup and "$env:GITHUB_PATH" in setup


def test_msvc_configuration_survives_process_boundary(tmp_path: Path) -> None:
    # Exercise the actual workflow persistence block with fixture MSVC values.
    # This proves handoff serialization, not availability of hosted MSVC.
    pwsh = shutil.which("pwsh")
    assert pwsh, "Windows workflow persistence regression needs PowerShell"
    for name in ("rust", "node"):
        step = next(s for s in workflow()["jobs"][name]["steps"] if s.get("name") == "Enable installed MSVC tools")
        block = step["run"][step["run"].index("foreach ($key"):]
        env_file = tmp_path / f"{name}-env"
        path_file = tmp_path / f"{name}-path"
        env = dict(os.environ, GITHUB_ENV=str(env_file), GITHUB_PATH=str(path_file))
        for key in ("INCLUDE", "LIB", "LIBPATH", "VCToolsInstallDir", "VCINSTALLDIR", "WindowsSdkDir", "WindowsSDKVersion", "VSCMD_ARG_TGT_ARCH"):
            env[key] = f"fixture-{key}"
        env["PATH"] = r"C:\fixture-msvc;" + env["PATH"]
        block = r'$msvcLinker = "C:\fixture-msvc\link.exe"; ' + block
        env["CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER"] = r"C:\fixture-msvc\link.exe"
        subprocess.run([pwsh, "-NoProfile", "-Command", block], env=env, check=True, capture_output=True, timeout=30)
        next_env = dict(os.environ)
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            key, value = line.split("=", 1)
            next_env[key] = value
        entries = path_file.read_text(encoding="utf-8-sig").splitlines()
        assert r"C:\fixture-msvc" in entries
        next_env["PATH"] = ";".join(entries)
        result = subprocess.run([pwsh, "-NoProfile", "-Command", "[pscustomobject]@{Include=$env:INCLUDE;Lib=$env:LIB;LibPath=$env:LIBPATH;Tools=$env:VCToolsInstallDir;Path=$env:PATH} | ConvertTo-Json -Compress"], env=next_env, check=True, capture_output=True, text=True, timeout=30)
        actual = json.loads(result.stdout)
        assert actual["Include"] == "fixture-INCLUDE"
        assert actual["Lib"] == "fixture-LIB"
        assert actual["LibPath"] == "fixture-LIBPATH"
        assert actual["Tools"] == "fixture-VCToolsInstallDir"
        assert r"C:\fixture-msvc" in actual["Path"].split(";")


def test_required_opa_tap_pattern_rejects_skips_and_failures() -> None:
    name = "zero-config fromPath uses bundled opa with an empty PATH"
    pattern = rf"(?m)^ok \d+ - {re.escape(name)}\r?$"
    assert re.search(pattern, f"ok 20 - {name}\r\n")
    assert not re.search(pattern, f"ok 20 - {name} # SKIP\n")
    assert not re.search(pattern, f"not ok 20 - {name}\n")


@pytest.mark.parametrize("job", ["rust", "node"])
def test_native_pins_msvc_linker_across_steps(tmp_path: Path, job: str) -> None:
    steps = workflow()["jobs"][job]["steps"]
    setup = next(s["run"] for s in steps if s.get("name") == "Enable installed MSVC tools")
    assert "Join-Path $env:VCToolsInstallDir 'bin/Hostx64/x64/link.exe'" in setup
    assert "Test-Path -LiteralPath $msvcLinker -PathType Leaf" in setup
    assert "'CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER'" in setup
    build_name = "Build locked Rust workspace" if job == "rust" else "Build once and test native SDK with bundled OPA"
    assert steps.index(next(s for s in steps if s.get("name") == "Enable installed MSVC tools")) < steps.index(next(s for s in steps if s.get("name") == build_name))
    assert "$env:PATH.Split" not in setup
    assert "Split-Path -Parent $msvcLinker" in setup
    assert "IsPathFullyQualified" in setup and "Unexpected non-MSVC linker path" in setup
    # Exercise resolution/persistence with a Git linker present earlier in PATH.
    # No compiler or linker is executed by this fixture.
    pwsh = shutil.which("pwsh")
    assert pwsh
    tools = tmp_path / "msvc-tools"
    linker = tools / "bin/Hostx64/x64/link.exe"
    linker.parent.mkdir(parents=True)
    linker.touch()
    git_bin = tmp_path / "git-bin"
    git_bin.mkdir()
    (git_bin / "link.exe").touch()
    env_file, path_file = tmp_path / "env", tmp_path / "path"
    env = dict(os.environ, VCToolsInstallDir=str(tools), GITHUB_ENV=str(env_file), GITHUB_PATH=str(path_file))
    env["PATH"] = str(git_bin) + ";" + env["PATH"]
    block = setup[setup.index("$msvcLinker ="):]
    subprocess.run([pwsh, "-NoProfile", "-Command", block], env=env, check=True, capture_output=True, timeout=30)
    next_env = dict(os.environ, PATH=env["PATH"])
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        key, value = line.split("=", 1)
        next_env[key] = value
    # Model runner behavior that prepends each GITHUB_PATH entry.
    entries = path_file.read_text(encoding="utf-8-sig").splitlines()
    assert entries == [str(linker.parent)]
    for entry in entries:
        next_env["PATH"] = entry + ";" + next_env["PATH"]
    result = subprocess.run([pwsh, "-NoProfile", "-Command", "[pscustomobject]@{CargoLinker=$env:CARGO_TARGET_X86_64_PC_WINDOWS_MSVC_LINKER;DefaultLinker=(Get-Command link.exe -ErrorAction Stop).Source} | ConvertTo-Json -Compress"], env=next_env, check=True, capture_output=True, text=True, timeout=30)
    actual = json.loads(result.stdout)
    assert Path(actual["DefaultLinker"]) == linker
    assert Path(actual["CargoLinker"]) == linker
