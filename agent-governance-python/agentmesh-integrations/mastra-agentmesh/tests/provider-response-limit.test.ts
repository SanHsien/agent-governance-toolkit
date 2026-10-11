// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
import { describe, expect, it } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { z } from 'zod';
import { sha256, transformSource } from '../scripts/patch-provider-utils.mjs';

const require = createRequire(import.meta.url);
const coreRequire = createRequire(require.resolve('@mastra/core'));
const uiRequire = createRequire(coreRequire.resolve('@ai-sdk/ui-utils-v5'));
const legacy = uiRequire('@ai-sdk/provider-utils');
const legacyPath = uiRequire.resolve('@ai-sdk/provider-utils/package.json');
const cap = 8 * 1024 * 1024;
const params = (response: Response) => ({ response, url: 'https://offline.invalid/fixture', requestBodyValues: {} });

function streamFixture(chunks: Uint8Array[], headers: Record<string, string> = {}, cancelError = false) {
  let cancelled = 0;
  const response = new Response(new ReadableStream<Uint8Array>({
    start(controller) { for (const chunk of chunks) controller.enqueue(chunk); },
    cancel() { cancelled++; if (cancelError) throw new Error('fixture cancellation failed'); },
  }), { headers });
  return { response, cancelled: () => cancelled };
}

async function formats() {
  return [legacy, await import(pathToFileURL(path.join(path.dirname(legacyPath), 'dist/index.mjs')).href)];
}

describe('fork legacy provider-utils bounded response backport', () => {
  it('keeps original package identity and synchronous ui-utils parsing', () => {
    expect(JSON.parse(fs.readFileSync(legacyPath, 'utf8')).version).toBe('2.2.8');
    const ui = coreRequire('@ai-sdk/ui-utils-v5');
    expect(ui.parsePartialJson('{"ok":true}')).toEqual({ value: { ok: true }, state: 'successful-parse' });
    expect(ui.parsePartialJson('{"ok":')).toMatchObject({ state: 'repaired-parse' });
    expect(legacy.safeParseJSON({ text: '{"ok":true}' })).toMatchObject({ success: true, value: { ok: true } });
    expect(legacy.safeParseJSON({ text: '{"ok":true}' })).not.toBeInstanceOf(Promise);
  });

  it('preserves normal JSON, UTF-8, empty/text errors and structured JSON errors in CJS/ESM', async () => {
    for (const api of await formats()) {
      const schema = z.object({ message: z.string() });
      const json = await api.createJsonResponseHandler(schema)(params(new Response('{"message":"繁體😀"}')));
      expect(json.value).toEqual({ message: '繁體😀' });
      const status = await api.createStatusCodeErrorResponseHandler()(params(new Response('ordinary text', { status: 503, statusText: 'Unavailable' })));
      expect(status.value.responseBody).toBe('ordinary text');
      expect(status.value.statusCode).toBe(503);
      const error = api.createJsonErrorResponseHandler({ errorSchema: schema, errorToMessage: (value: { message: string }) => value.message });
      expect((await error(params(new Response('{"message":"denied"}', { status: 403 })))).value.message).toBe('denied');
      expect((await error(params(new Response(null, { status: 500, statusText: 'Empty' })))).value.message).toBe('Empty');
      await expect(api.createJsonResponseHandler(schema)(params(new Response('not json')))).rejects.toThrow('Invalid JSON response');
    }
  });

  it('rejects oversized Content-Length before reading and cancels all three affected handlers', async () => {
    for (const api of await formats()) {
      const schema = z.object({ ok: z.boolean() });
      const handlers = [api.createJsonResponseHandler(schema), api.createStatusCodeErrorResponseHandler(), api.createJsonErrorResponseHandler({ errorSchema: schema, errorToMessage: () => 'error' })];
      for (const handler of handlers) {
        const fixture = streamFixture([new TextEncoder().encode('{"ok":true}')], { 'content-length': String(cap + 1) });
        await expect(handler(params(fixture.response))).rejects.toThrow(/exceeds fork limit/);
        expect(fixture.cancelled()).toBe(1);
        expect(fixture.response.body!.locked).toBe(false);
      }
    }
  });

  it.each([{}, { 'content-length': '1' }, { 'content-length': 'invalid' }])('enforces actual byte count with absent/misleading header %j', async headers => {
    const fixture = streamFixture([new Uint8Array(cap), new Uint8Array(1)], headers);
    await expect(legacy.createStatusCodeErrorResponseHandler()(params(fixture.response))).rejects.toThrow(/exceeds fork limit/);
    expect(fixture.cancelled()).toBe(1);
    expect(fixture.response.body!.locked).toBe(false);
  });

  it('counts UTF-8 bytes rather than JS characters and preserves errors if cancellation fails', async () => {
    const bytes = new TextEncoder().encode('😀'.repeat(cap / 4 + 1));
    expect(bytes.byteLength).toBe(cap + 4);
    const fixture = streamFixture([bytes], {}, true);
    await expect(legacy.createStatusCodeErrorResponseHandler()(params(fixture.response))).rejects.toThrow(/exceeds fork limit/);
    expect(fixture.cancelled()).toBe(1);
    expect(fixture.response.body!.locked).toBe(false);
  });

  it('accepts the byte boundary and releases the lock after normal completion', async () => {
    const response = new Response(new Uint8Array(cap));
    expect((await legacy.createStatusCodeErrorResponseHandler()(params(response))).value.responseBody.length).toBe(cap);
    expect(response.body!.locked).toBe(false);
  });

  it('preserves abort errors and releases the reader lock', async () => {
    const response = new Response(new ReadableStream({ start(controller) { controller.error(new DOMException('fixture abort', 'AbortError')); } }));
    await expect(legacy.createStatusCodeErrorResponseHandler()(params(response))).rejects.toMatchObject({ name: 'AbortError' });
    expect(response.body!.locked).toBe(false);
  });

  it('applies only hash-bound bytes, rejects unknown input/output/context and is idempotent', () => {
    const before = Buffer.from('original');
    const after = Buffer.from('bounded');
    const spec = { path: 'fixture', before_sha256: sha256(before), after_sha256: sha256(after), replacements: [{ before: 'original', after: 'bounded', count: 1 }] };
    expect(transformSource(before, spec)).toEqual(after);
    expect(transformSource(after, spec, true)).toEqual(after);
    expect(() => transformSource(before, spec, true)).toThrow(/Unverified/);
    expect(() => transformSource(Buffer.from('unknown'), spec)).toThrow(/Unverified/);
    expect(() => transformSource(before, { ...spec, after_sha256: '0'.repeat(64) })).toThrow(/output hash/);
    expect(() => transformSource(before, { ...spec, replacements: [{ ...spec.replacements[0], count: 2 }] })).toThrow(/context/);
  });

  it('uses patched same-major v5/v6 aliases with real bounded response handlers', async () => {
    for (const [alias, version] of [['@ai-sdk/provider-utils-v5', '3.0.28'], ['@ai-sdk/provider-utils-v6', '4.0.33']]) {
      expect(coreRequire(`${alias}/package.json`).version).toBe(version);
      const api = coreRequire(alias);
      const normal = await api.createJsonResponseHandler(z.object({ ok: z.boolean() }))(params(new Response('{"ok":true}')));
      expect(normal.value).toEqual({ ok: true });
      const fixture = streamFixture([new Uint8Array(1)], { 'content-length': String(2 * 1024 * 1024 * 1024 + 1) });
      await expect(api.createStatusCodeErrorResponseHandler()(params(fixture.response))).rejects.toThrow(/maximum size/);
      expect(fixture.cancelled()).toBe(1);
    }
  });
});
