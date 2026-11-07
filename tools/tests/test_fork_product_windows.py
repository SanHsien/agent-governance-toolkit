from __future__ import annotations

import codecs
import json
import os
import re
import shutil
import subprocess
import sys
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
    assert "agent-governance-python/agent-sre/**" in doc["on"]["push"]["paths"]
    assert "agent-governance-python/agent-lightning/**" in doc["on"]["push"]["paths"]
    assert set(doc["jobs"]) == {"rust", "copilot", "node", "typescript", "mastra", "agent-sre", "agent-lightning"}
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


@pytest.mark.parametrize("name,directory,command", [
    ("typescript", "agent-governance-typescript", "npm test -- --runInBand"),
    ("mastra", "agent-governance-python/agentmesh-integrations/mastra-agentmesh", "npm test"),
])
def test_additional_windows_dependency_consumers(name: str, directory: str, command: str) -> None:
    doc = workflow()
    assert directory + "/**" in doc["on"]["push"]["paths"]
    job = doc["jobs"][name]
    assert job["timeout-minutes"] == "20"
    assert job["defaults"]["run"]["working-directory"] == directory
    assert next(s for s in job["steps"] if s.get("uses", "").startswith("actions/setup-node@"))["with"]["node-version"] == "22"
    steps = [s for s in job["steps"] if "run" in s]
    assert [s["run"] for s in steps] == (["npm ci --ignore-scripts"] + (["npm run patch:dependencies && node scripts/patch-provider-utils.mjs --check"] if name == "mastra" else []) + ["npm run build"] + (["npm run lint"] if name == "mastra" else []) + [command, "git diff --exit-code -- package.json package-lock.json"])
    assert all(0 < int(s["timeout-minutes"]) <= 10 for s in steps[:-1])


def test_mastra_backport_install_contract_and_artifact_binding() -> None:
    import hashlib

    directory = ROOT / "agent-governance-python/agentmesh-integrations/mastra-agentmesh"
    package = json.loads((directory / "package.json").read_text())
    assert "install" not in package["scripts"]
    assert "postinstall" not in package["scripts"]
    assert package["files"] == ["dist"]
    lock = json.loads((directory / "package-lock.json").read_text())
    assert not lock["packages"][""].get("hasInstallScript", False)
    for name in ("prebuild", "pretest", "prelint"):
        assert package["scripts"][name] == "npm run patch:dependencies"
    artifact_path = directory / "patches/provider-utils-2.2.8-response-limit.json"
    artifact_bytes = artifact_path.read_bytes()
    assert b"\r\n" not in artifact_bytes, "Artifact must use checkout-stable LF bytes"
    relative_path = artifact_path.relative_to(ROOT).as_posix()
    clean_blob = subprocess.check_output(
        ["git", "hash-object", f"--path={relative_path}", "--stdin"],
        input=artifact_bytes, cwd=ROOT,
    ).strip()
    raw_blob = subprocess.check_output(
        ["git", "hash-object", "--no-filters", "--stdin"],
        input=artifact_bytes, cwd=ROOT,
    ).strip()
    assert clean_blob == raw_blob, "Git clean filters must preserve the bound artifact bytes"
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    script = (directory / "scripts/patch-provider-utils.mjs").read_text(encoding="utf-8-sig")
    assert f"const artifactSha256 = '{digest}'" in script
    artifact = json.loads(artifact_path.read_text())
    assert artifact["package"] == "@ai-sdk/provider-utils"
    assert artifact["version"] == "2.2.8"
    assert artifact["max_response_bytes"] == 8 * 1024 * 1024
    assert [f["path"] for f in artifact["files"]] == ["dist/index.js", "dist/index.mjs"]
    assert all(re.fullmatch("[0-9a-f]{64}", f[k]) for f in artifact["files"] for k in ("before_sha256", "after_sha256"))


PYTHON_JOBS = {
    "agent-sre": "agent-governance-python/agent-sre",
    "agent-lightning": "agent-governance-python/agent-lightning",
}


@pytest.mark.parametrize("name,directory", sorted(PYTHON_JOBS.items()))
def test_python_package_jobs_run_full_suite(name: str, directory: str) -> None:
    doc = workflow()
    assert directory + "/**" in doc["on"]["push"]["paths"]
    assert directory + "/**" in doc["on"]["pull_request"]["paths"]
    job = doc["jobs"][name]
    assert job["timeout-minutes"] == "20"
    assert job["defaults"]["run"]["working-directory"] == directory
    assert next(s for s in job["steps"] if s.get("uses", "").startswith("actions/setup-python@"))["with"]["python-version"] == "3.13"
    steps = [s for s in job["steps"] if "run" in s]
    assert all(0 < int(s["timeout-minutes"]) <= 10 for s in steps)
    # The whole suite must run: the exact command has no path narrowing, marker
    # filter or --deselect, so a new failure cannot be hidden by excluding it.
    test_step = steps[-1]
    assert test_step["run"] == "python -m pytest tests -q --tb=short -p no:cacheprovider"
    assert test_step["env"]["PYTHONUTF8"] == "1"
    assert "continue-on-error" not in job and not any("continue-on-error" in s for s in job["steps"])


def test_agent_sre_imports_source_tree_and_installs_dev_extra() -> None:
    steps = {s["name"]: s for s in workflow()["jobs"]["agent-sre"]["steps"] if "name" in s}
    # The stub's `.[dev]` install would resolve agent-governance-toolkit-core, whose
    # pre-release dependency is not on PyPI; the tree under test comes from PYTHONPATH.
    assert steps["Run agent-sre tests"]["env"]["PYTHONPATH"] == "src"
    install = steps["Install test dependencies"]["run"]
    assert 'dev-requirements.txt' in install and "httpx" in install and "cryptography" in install
    assert "-e " not in install and "--deselect" not in install


def test_agent_lightning_installs_editable_dev_extra() -> None:
    steps = {s["name"]: s for s in workflow()["jobs"]["agent-lightning"]["steps"] if "name" in s}
    assert "python -m pip install --no-cache-dir -e '.[dev]'" in steps["Install package with dev extra"]["run"]
    assert "PYTHONPATH" not in steps["Run agent-lightning tests"].get("env", {})


def test_agent_sre_dev_extra_resolution_matches_pyproject(tmp_path: Path) -> None:
    # Run the real workflow step (pwsh + embedded Python) and compare with pyproject.
    import tomllib

    pwsh = shutil.which("pwsh")
    assert pwsh, "dev extra resolution regression needs PowerShell"
    step = next(s for s in workflow()["jobs"]["agent-sre"]["steps"] if s.get("name") == "Resolve dev extra from pyproject")
    directory = ROOT / PYTHON_JOBS["agent-sre"]
    env = dict(os.environ, RUNNER_TEMP=str(tmp_path))
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env["PATH"]
    subprocess.run([pwsh, "-NoProfile", "-Command", step["run"]], cwd=directory, env=env, check=True, capture_output=True, timeout=60)
    expected = tomllib.loads((directory / "pyproject.toml").read_text(encoding="utf-8"))["project"]["optional-dependencies"]["dev"]
    raw = (tmp_path / "dev-requirements.txt").read_bytes()
    assert not raw.startswith(codecs.BOM_UTF8)
    assert raw.decode("utf-8").splitlines() == expected
    assert any(line.startswith("pytest") for line in expected)

def test_hono_node_server_advisory_remediation_and_lock_integrity() -> None:
    # GHSA-rmxm-3fg6-px4f / CVE-2026-118663 remediation:
    # @hono/node-server must be >= 2.1.3 (first patched release) in both lockfiles.
    # Lockfiles must maintain peerDependencies sync without dropping required packages.
    def parse_version(v: str) -> tuple[int, ...]:
        clean = v.split("-")[0]
        return tuple(int(x) for x in clean.split("."))

    for rel_path in (
        "agent-governance-python/agentmesh-integrations/mastra-agentmesh",
        "policy-engine/sdk/node",
        "agent-governance-python/agent-os/extensions/mcp-server",
        "agent-governance-python/agent-mesh/packages/mcp-proxy",
    ):
        dir_path = ROOT / rel_path
        pkg = json.loads((dir_path / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((dir_path / "package-lock.json").read_text(encoding="utf-8"))
        override_version = pkg.get("overrides", {}).get("@hono/node-server")
        assert override_version is not None, f"Missing @hono/node-server override in {rel_path}"

        packages = lock.get("packages", {})
        hono_entry = packages.get("node_modules/@modelcontextprotocol/sdk/node_modules/@hono/node-server") or packages.get("node_modules/@hono/node-server")
        assert hono_entry is not None, f"Missing @hono/node-server entry in {rel_path} lockfile"
        lock_version = hono_entry.get("version", "")
        assert parse_version(lock_version) >= (2, 1, 3), f"@hono/node-server {lock_version} in {rel_path} is vulnerable (< 2.1.3)"
        assert override_version == lock_version, f"Override ({override_version}) does not match lock ({lock_version}) in {rel_path}"

    # The 2.x line needs Node >= 20 and it is a runtime dependency (via the MCP SDK) of the two
    # MCP server packages, so their declared engines must not promise Node 18.
    for rel_path in (
        "agent-governance-python/agent-os/extensions/mcp-server",
        "agent-governance-python/agent-mesh/packages/mcp-proxy",
    ):
        dir_path = ROOT / rel_path
        pkg = json.loads((dir_path / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((dir_path / "package-lock.json").read_text(encoding="utf-8"))
        hono_engine = lock["packages"]["node_modules/@hono/node-server"]["engines"]["node"]
        required = int(re.search(r"\d+", hono_engine).group())
        declared_engine = pkg["engines"]["node"]
        declared = int(re.search(r"\d+", declared_engine).group())
        assert declared >= required, f"{rel_path} declares node {declared_engine} but @hono/node-server needs {hono_engine}"
        assert lock["packages"][""]["engines"]["node"] == declared_engine, f"{rel_path} lock root engines is out of sync with package.json"

    # policy-engine/sdk/node keeps engines >=18 only while hono stays dev-only/optional (reached via
    # the optional MCP SDK peer in devDependencies) and the package has no runtime "dependencies".
    # If hono ever becomes a runtime dependency there, engines must be raised to the 2.x requirement.
    sdk_dir = ROOT / "policy-engine/sdk/node"
    sdk_pkg = json.loads((sdk_dir / "package.json").read_text(encoding="utf-8"))
    sdk_lock = json.loads((sdk_dir / "package-lock.json").read_text(encoding="utf-8"))
    sdk_hono = sdk_lock["packages"].get("node_modules/@hono/node-server")
    assert sdk_hono is not None, (
        "policy-engine/sdk/node lock has no node_modules/@hono/node-server entry; "
        "drop this engines check together with the dependency, or restore the lock entry"
    )
    sdk_declared = int(re.search(r"\d+", sdk_pkg["engines"]["node"]).group())
    sdk_required = int(re.search(r"\d+", sdk_hono["engines"]["node"]).group())
    if not (sdk_hono.get("dev") and sdk_hono.get("optional") and "dependencies" not in sdk_pkg):
        assert sdk_declared >= sdk_required, "policy-engine/sdk/node hono is no longer dev-only; raise engines.node"
    assert sdk_lock["packages"][""]["engines"]["node"] == sdk_pkg["engines"]["node"], (
        "policy-engine/sdk/node package-lock.json root engines.node differs from package.json; "
        "run npm install to resync the lock"
    )

    mastra_lock = json.loads(
        (ROOT / "agent-governance-python/agentmesh-integrations/mastra-agentmesh/package-lock.json").read_text(encoding="utf-8")
    )
    # Regression against Dependabot PR #57 lock pruning bug:
    assert "node_modules/@standard-community/standard-json" in mastra_lock.get("packages", {})


def test_minimatch_advisory_remediation_leaves_no_vulnerable_lock_entry() -> None:
    # GHSA-g3hv-75wg-m249 / CVE-2026-118764: minimatch >= 7.0.0, < 11.0.1 is vulnerable.
    # Property: no minimatch entry anywhere in the lockfile (including nested copies pulled in
    # by glob) may sit in the vulnerable range, and the root copy is the patched 11.0.1.
    # minimatch 3.x is deliberately left alone for test-exclude: it calls require("minimatch")
    # as a function, which 11.x (an object export) breaks under `jest --coverage`.
    # @isaacs/nonrecursive-glob-match is pinned to 1.0.3 to respect the seven-day cooling-off.
    def parse_version(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split("-")[0].split("."))

    for rel_path in (
        "agent-governance-python/agent-os/extensions/mcp-server",
        "agent-governance-python/agent-os/extensions/copilot",
        "agent-governance-typescript",
    ):
        dir_path = ROOT / rel_path
        pkg = json.loads((dir_path / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((dir_path / "package-lock.json").read_text(encoding="utf-8"))
        overrides = pkg.get("overrides", {})
        assert any(key == "minimatch" or key.startswith("minimatch@") for key in overrides), f"Missing minimatch override in {rel_path}"
        assert overrides.get("@isaacs/nonrecursive-glob-match") == "1.0.3", f"Missing cooling-off pin in {rel_path}"

        packages = lock.get("packages", {})
        assert packages["node_modules/minimatch"]["version"] == "11.0.1", f"Root minimatch is not 11.0.1 in {rel_path}"
        assert packages["node_modules/@isaacs/nonrecursive-glob-match"]["version"] == "1.0.3", f"Unpinned nonrecursive-glob-match in {rel_path}"
        for key, entry in packages.items():
            if key == "node_modules/minimatch" or key.endswith("/node_modules/minimatch"):
                version = entry.get("version", "")
                assert not (
                    (7, 0, 0) <= parse_version(version) < (11, 0, 1)
                ), f"{key} {version} in {rel_path} is vulnerable (>= 7.0.0, < 11.0.1)"

    for rel_path in ("agent-governance-typescript", "agent-governance-python/agent-os/extensions/copilot"):
        jest_lock = json.loads((ROOT / rel_path / "package-lock.json").read_text(encoding="utf-8"))
        test_exclude = jest_lock["packages"].get("node_modules/test-exclude/node_modules/minimatch")
        assert test_exclude is not None and parse_version(test_exclude["version"]) < (7, 0, 0), (
            f"test-exclude must keep its CommonJS-function minimatch 3.x copy in {rel_path} (jest --coverage)"
        )

    # npm 10 (bundled with the Node 22 used by CI) does not apply range-keyed overrides such as
    # "minimatch@^10" to every nested consumer (it left rimraf's glob 13 on minimatch 10.2.6 and
    # `npm ci` failed with "Missing: minimatch@10.2.6 from lock file"). The TypeScript SDK therefore
    # uses a global pin plus an explicit test-exclude exemption, which both npm 10 and 11 resolve alike.
    ts_overrides = json.loads((ROOT / "agent-governance-typescript/package.json").read_text(encoding="utf-8"))["overrides"]
    assert ts_overrides.get("minimatch") == "11.0.1"
    assert ts_overrides.get("test-exclude", {}).get("minimatch") == "3.1.5"


def _lock_versions(lock: dict, name: str) -> list[tuple[str, str]]:
    return [
        (key, entry.get("version", ""))
        for key, entry in lock.get("packages", {}).items()
        if key == f"node_modules/{name}" or key.endswith(f"/node_modules/{name}")
    ]


def test_follow_redirects_advisory_remediation_leaves_no_vulnerable_lock_entry() -> None:
    # GHSA-mrwp-f3q8-3g9p / CVE-2026-116689: follow-redirects >= 1.16.0, <= 1.16.1 is vulnerable
    # (first patched 1.16.2). axios asks for ^1.16.0, so a plain lock refresh is enough and no
    # override is needed; the property is that no lock entry sits in the vulnerable range.
    lock = json.loads(
        (ROOT / "agent-governance-python/agent-os/extensions/copilot/package-lock.json").read_text(encoding="utf-8")
    )
    entries = _lock_versions(lock, "follow-redirects")
    assert entries, "copilot extension no longer locks follow-redirects; update this test"
    for key, version in entries:
        parts = tuple(int(x) for x in version.split("-")[0].split("."))
        assert not ((1, 16, 0) <= parts <= (1, 16, 1)), f"{key} {version} is vulnerable (>= 1.16.0, <= 1.16.1)"


def test_pypdf_advisory_remediation_pins_patched_release_in_every_caas_manifest() -> None:
    # GHSA-x3rh-gjgm-fmqc and six sibling pypdf advisories (published 2026-10-30): everything below
    # 6.21.4 is affected. The caas image installs requirements.txt; requirements.lock is the
    # hash-pinned copy and must not lag behind it, and pyproject must still admit the pin.
    caas = ROOT / "agent-governance-python/agent-os/modules/caas"
    txt = (caas / "requirements.txt").read_text(encoding="utf-8")
    pinned = re.search(r"^pypdf==(\d+)\.(\d+)\.(\d+)\b", txt, re.MULTILINE)
    assert pinned is not None, "caas requirements.txt must pin pypdf exactly"
    version = tuple(int(x) for x in pinned.groups())
    assert (6, 21, 4) <= version < (7, 0, 0), f"pypdf {version} is vulnerable or crosses the <7.0 cap in pyproject"

    lock = (caas / "requirements.lock").read_text(encoding="utf-8")
    locked = re.search(r"^pypdf==(\S+) \\\n((?:\s+--hash=sha256:[0-9a-f]{64}(?: \\)?\n?)+)", lock, re.MULTILINE)
    assert locked is not None, "caas requirements.lock must carry a hash-pinned pypdf block"
    assert locked.group(1) == ".".join(map(str, version)), "requirements.lock pypdf differs from requirements.txt"
    assert len(re.findall(r"--hash=sha256:", locked.group(2))) >= 2, "pypdf needs wheel and sdist hashes"

    pyproject = (caas / "pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'"pypdf>=[\d.]+,<7\.0"', pyproject), "pyproject pypdf range changed; re-check the pin"


def test_cedar_policy_advisory_remediation_leaves_no_vulnerable_cargo_lock() -> None:
    # GHSA-c33x-vcv4-vg3g: cedar-policy >= 4.0.0, < 4.11.1 is vulnerable (first patched 4.11.1).
    # Property over every tracked Cargo.lock, not only the one Dependabot flagged, and the three
    # cedar crates must move together (cedar-policy pins its core and formatter exactly).
    tracked = subprocess.run(
        ["git", "ls-files", "*Cargo.lock"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.split()
    checked = 0
    for rel in tracked:
        text = (ROOT / rel).read_text(encoding="utf-8")
        versions = dict(re.findall(r'name = "(cedar-policy(?:-core|-formatter)?)"\nversion = "([^"]+)"', text))
        if "cedar-policy" not in versions:
            continue
        checked += 1
        parts = tuple(int(x) for x in versions["cedar-policy"].split("."))
        assert parts >= (4, 11, 1), f"{rel} locks cedar-policy {versions['cedar-policy']} (< 4.11.1)"
        assert len(set(versions.values())) == 1, f"{rel} has mismatched cedar crate versions {versions}"
    assert checked >= 2, "expected several Cargo.lock files to carry cedar-policy"


def test_deepmerge_unpatched_advisory_is_only_tolerated_with_a_dated_deferral() -> None:
    # GHSA-gcqx-w48m-w2h4 / CVE-2026-93753: deepmerge <= 4.3.1 has no patched release (npm latest is
    # 4.3.1). It is a dev-only dependency of jest-config. While any lock still resolves a vulnerable
    # deepmerge, the audit trail must carry a dated deferral with a reopen condition; once every
    # lock is above 4.3.1 the deferral is moot.
    vulnerable = []
    for rel in (
        "agent-governance-typescript/package-lock.json",
        "agent-governance-python/agent-os/extensions/copilot/package-lock.json",
    ):
        lock = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        for key, version in _lock_versions(lock, "deepmerge"):
            parts = tuple(int(x) for x in version.split("."))
            assert lock["packages"][key].get("dev") is True, f"{rel} {key} is no longer dev-only; revisit the deferral"
            if (4, 2, 0) <= parts <= (4, 3, 1):
                vulnerable.append((rel, version))
    if not vulnerable:
        return
    audit = (ROOT / "docs/dependency-audits/2026-11-07-npm-hono-follow-redirects-deepmerge.md").read_text(encoding="utf-8")
    assert "GHSA-gcqx-w48m-w2h4" in audit and "#292" in audit and "#286" in audit
    assert "Deferred since 2026-10-29" in audit, "deepmerge deferral must be dated"
    assert "Reopen when" in audit, "deepmerge deferral must state its reopen condition"
    decisions = (ROOT / "docs/fork/DECISIONS.md").read_text(encoding="utf-8")
    assert "## 2026-10-29：deepmerge 延後項目重查" in decisions, "the original dated deferral entry went missing"
