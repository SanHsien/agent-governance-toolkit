// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { Workspace, LocalFilesystem } from '@mastra/core/workspace';

const require = createRequire(import.meta.url);
const coreRequire = createRequire(require.resolve('@mastra/core/workspace'));
const matterPath = coreRequire.resolve('gray-matter');
const matter = coreRequire('gray-matter');
const yaml = '---\nname: offline-skill\ndescription: Local regression fixture\nuser-invocable: false\nmetadata:\n  tags: [alpha, beta]\n  enabled: true\n  count: 2\n  date: 2026-10-11\n---\n# Offline instructions\nPreserve Markdown body.\n';

describe('fork Mastra skill front matter dependency repair', () => {
  let fixture: string;
  beforeEach(() => { fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'agt-mastra-skill-')); });
  afterEach(() => fs.rmSync(fixture, { recursive: true, force: true }));

  it('scopes the maintained alias to Mastra and removes sprintf from the lock', () => {
    const root = path.resolve(import.meta.dirname, '..');
    const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
    const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
    expect(manifest.overrides['@mastra/core']['gray-matter']).toBe('npm:@11ty/gray-matter@3.0.0');
    expect(manifest.overrides['gray-matter']).toBeUndefined();
    const installed = JSON.parse(fs.readFileSync(coreRequire.resolve('gray-matter/package.json'), 'utf8'));
    expect([installed.name, installed.version]).toEqual(['@11ty/gray-matter', '3.0.0']);
    expect(Object.keys(lock.packages).filter(key => key.endsWith('node_modules/sprintf-js'))).toEqual([]);
  });

  it('preserves data/content and ordinary YAML schema through CJS and ESM imports', async () => {
    const esm = (await import(pathToFileURL(matterPath).href)).default;
    for (const parse of [matter, esm]) {
      const parsed = parse(yaml);
      expect(parsed.data).toMatchObject({ name: 'offline-skill', 'user-invocable': false, metadata: { tags: ['alpha', 'beta'], enabled: true, count: 2, date: '2026-10-11' } });
      expect(parsed.content.trim()).toBe('# Offline instructions\nPreserve Markdown body.');
      expect(parse(Buffer.from(yaml)).data).toEqual(parsed.data);
    }
  });

  it('loads real offline SKILL.md through the Mastra Workspace consumer', async () => {
    const dir = path.join(fixture, 'skills', 'offline-skill');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'SKILL.md'), yaml);
    const workspace = new Workspace({ filesystem: new LocalFilesystem({ basePath: fixture }), skills: ['skills'] });
    const skill = await workspace.skills!.get('offline-skill');
    expect(skill).toMatchObject({ name: 'offline-skill', description: 'Local regression fixture', 'user-invocable': false, metadata: { tags: ['alpha', 'beta'], enabled: true, count: 2, date: '2026-10-11' }, instructions: '# Offline instructions\nPreserve Markdown body.' });
  });

  it('rejects JavaScript front matter without executing its payload', async () => {
    const marker = path.join(fixture, 'must-not-exist');
    const payload = `---js\n(function(){ require('node:fs').writeFileSync(${JSON.stringify(marker)}, 'executed'); return {name:'unsafe-skill', description:'unsafe'}; })()\n---\nBody\n`;
    expect(() => matter(payload)).toThrow(/JavaScript.*no longer supported/);
    const dir = path.join(fixture, 'skills', 'unsafe-skill');
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'SKILL.md'), payload);
    const workspace = new Workspace({ filesystem: new LocalFilesystem({ basePath: fixture }), skills: ['skills'] });
    expect(await workspace.skills!.get('unsafe-skill')).toBeNull();
    expect(fs.existsSync(marker)).toBe(false);
  });
});
