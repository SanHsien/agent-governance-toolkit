// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import { expect, it } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

it('packs the dist-only consumer contract without a missing dependency install hook', () => {
  const evidenceDirectory = process.env.AGT_PACK_EVIDENCE_DIR;
  const destination = evidenceDirectory || fs.mkdtempSync(path.join(os.tmpdir(), 'agt-mastra-pack-contract-'));
  fs.mkdirSync(destination, { recursive: true });
  const root = path.resolve(import.meta.dirname, '..');
  try {
    const npmCli = process.env.npm_execpath;
    expect(npmCli, 'Run this regression through npm test').toBeTruthy();
    const output = execFileSync(process.execPath, [npmCli!, 'pack', '--ignore-scripts', '--json', '--pack-destination', destination], { cwd: root, encoding: 'utf8', timeout: 60_000 });
    const result = JSON.parse(output)[0];
    const tarball = path.join(destination, result.filename);
    const text = execFileSync(process.platform === 'win32' ? 'tar.exe' : 'tar', ['-xOf', tarball, 'package/package.json'], { encoding: 'utf8', timeout: 10_000 });
    const manifest = JSON.parse(text);
    expect(manifest.files).toEqual(['dist']);
    for (const name of ['preinstall', 'install', 'postinstall']) expect(manifest.scripts[name]).toBeUndefined();
    expect(result.files.some((file: { path: string }) => file.path === manifest.main)).toBe(true);
    expect(result.files.some((file: { path: string }) => /^(scripts|patches)\//.test(file.path))).toBe(false);
    const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
    expect(lock.packages[''].hasInstallScript).not.toBe(true);
    if (evidenceDirectory) fs.writeFileSync(path.join(destination, 'pack-contract-report.json'), JSON.stringify({ manifest, pack: result, tarball, sha256: crypto.createHash('sha256').update(fs.readFileSync(tarball)).digest('hex') }, null, 2));
  } finally {
    if (!evidenceDirectory) fs.rmSync(destination, { recursive: true, force: true });
  }
}, 90_000);
