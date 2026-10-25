// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';

const nycRequire = createRequire(require.resolve('@istanbuljs/load-nyc-config'));
const { loadNycConfig } = require('@istanbuljs/load-nyc-config');
const yamlPackage = nycRequire.resolve('js-yaml/package.json');
const yamlCli = path.join(path.dirname(yamlPackage), 'bin/js-yaml.js');

describe('fork coverage YAML dependency repair', () => {
  let fixture: string;
  beforeEach(() => {
    fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'agt-nyc-yaml-'));
    fs.writeFileSync(path.join(fixture, 'package.json'), '{"name":"offline-nyc-fixture"}');
  });
  afterEach(() => fs.rmSync(fixture, { recursive: true, force: true }));

  test('scopes the YAML override and eliminates the sprintf and handlebars dependencies', () => {
    const root = path.resolve(__dirname, '../..');
    const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
    const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
    expect(manifest.overrides['@istanbuljs/load-nyc-config']).toEqual({ 'js-yaml': '4.3.2' });
    expect(manifest.overrides['js-yaml']).toBeUndefined();
    expect(JSON.parse(fs.readFileSync(yamlPackage, 'utf8')).version).toBe('4.3.2');
    expect(Object.keys(lock.packages).filter(key => key.endsWith('node_modules/sprintf-js'))).toEqual([]);
    expect(lock.packages['node_modules/handlebars']).toBeUndefined();
  });

  test('loads real nyc YAML mappings and sequences', async () => {
    fs.writeFileSync(path.join(fixture, '.nycrc.yml'), 'all: true\ninclude:\n  - src/**/*.ts\nexclude:\n  - src/**/*.test.ts\nreporter:\n  - text\n  - json\n');
    const config = await loadNycConfig({ cwd: fixture });
    expect(config.all).toBe(true);
    expect(config.include).toEqual(['src/**/*.ts']);
    expect(config.exclude).toEqual(['src/**/*.test.ts']);
    expect(config.reporter).toEqual(['text', 'json']);
    expect(config.cwd).toBe(fixture);
  });

  test('resolves YAML extends and normalizes cwd relative to the extended file', async () => {
    const configs = path.join(fixture, 'configs');
    fs.mkdirSync(configs);
    fs.writeFileSync(path.join(configs, 'base.yml'), 'cwd: ../source-root\ncheck-coverage: true\nreporter:\n  - text\n  - json\n');
    fs.writeFileSync(path.join(fixture, '.nycrc.yml'), 'extends: ./configs/base.yml\ninclude:\n  - lib/**/*.ts\n');
    const config = await loadNycConfig({ cwd: fixture });
    expect(config.cwd).toBe(path.join(fixture, 'source-root'));
    expect(config.checkCoverage).toBe(true);
    expect(config.reporter).toEqual(['text', 'json']);
    expect(config.include).toEqual(['lib/**/*.ts']);
  });

  test('runs the actual YAML CLI help and fixture parser', () => {
    const help = execFileSync(process.execPath, [yamlCli, '--help'], { encoding: 'utf8', timeout: 10000 });
    expect(help).toMatch(/usage: js-yaml/i);
    const input = path.join(fixture, 'input.yml');
    fs.writeFileSync(input, 'enabled: true\nfiles:\n  - a.ts\n  - b.ts\n');
    const output = execFileSync(process.execPath, [yamlCli, input], { encoding: 'utf8', timeout: 10000 });
    expect(JSON.parse(output)).toEqual({ enabled: true, files: ['a.ts', 'b.ts'] });
  });
});
