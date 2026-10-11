// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const artifactPath = path.join(root, 'patches/provider-utils-2.2.8-response-limit.json');
const artifactSha256 = '073ab28e26233ad22400473e0fc95341d6ff2161ab23b33fb87ae7c3d96512a1';
export const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');

export function transformSource(source, spec, checkOnly = false) {
  const digest = sha256(source);
  if (digest === spec.after_sha256) return source;
  if (checkOnly || digest !== spec.before_sha256) throw new Error(`Unverified provider-utils input: ${spec.path}`);
  let result = source.toString('utf8');
  for (const replacement of spec.replacements) {
    if (!replacement.before || result.split(replacement.before).length - 1 !== replacement.count) {
      throw new Error(`Unexpected patch context: ${spec.path}`);
    }
    result = result.split(replacement.before).join(replacement.after);
  }
  const bytes = Buffer.from(result, 'utf8');
  if (sha256(bytes) !== spec.after_sha256) throw new Error(`Patch output hash mismatch: ${spec.path}`);
  return bytes;
}

export function patchDependencies(checkOnly = false) {
  const bytes = fs.readFileSync(artifactPath);
  if (sha256(bytes) !== artifactSha256) throw new Error('Unverified backport artifact');
  const artifact = JSON.parse(bytes);
  const require = createRequire(path.join(root, 'package.json'));
  const coreRequire = createRequire(require.resolve('@mastra/core'));
  const uiRequire = createRequire(coreRequire.resolve('@ai-sdk/ui-utils-v5'));
  const packagePath = uiRequire.resolve('@ai-sdk/provider-utils/package.json');
  const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  if (pkg.name !== artifact.package || pkg.version !== artifact.version) throw new Error('Unexpected legacy provider-utils version');
  for (const [name, version] of [['@ai-sdk/provider-utils-v5', '3.0.28'], ['@ai-sdk/provider-utils-v6', '4.0.33']]) {
    if (coreRequire(`${name}/package.json`).version !== version) throw new Error(`Unexpected patched alias: ${name}`);
  }
  const packageRoot = path.dirname(packagePath);
  if (artifact.files.length !== 2 || artifact.files.map(f => f.path).join(',') !== 'dist/index.js,dist/index.mjs') throw new Error('Unexpected patch targets');
  // Validate every input/output before writing either module format. Unknown bytes fail closed.
  const prepared = artifact.files.map(spec => {
    const target = path.join(packageRoot, spec.path);
    return { target, spec, bytes: transformSource(fs.readFileSync(target), spec, checkOnly) };
  });
  if (!checkOnly) for (const item of prepared) fs.writeFileSync(item.target, item.bytes);
  for (const { target, spec } of prepared) {
    if (sha256(fs.readFileSync(target)) !== spec.after_sha256) throw new Error(`Installed backport verification failed: ${spec.path}`);
  }
  console.log(JSON.stringify({ legacyVersion: pkg.version, patchedAliases: ['3.0.28', '4.0.33'], artifactSha256, maxResponseBytes: artifact.max_response_bytes, verified: true }));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.slice(2).some(arg => arg !== '--check')) throw new Error('Unsupported patch option');
  patchDependencies(process.argv.includes('--check'));
}
