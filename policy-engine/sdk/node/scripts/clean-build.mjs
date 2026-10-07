import { readdirSync, rmSync } from 'node:fs';

const generated = ['native.js', 'native.d.ts', ...readdirSync('.').filter((name) => name.endsWith('.node'))];
for (const path of generated) rmSync(path, { force: true });
if (!process.argv.includes('--generated-only')) rmSync('dist', { recursive: true, force: true });
