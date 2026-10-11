// Copyright (c) Microsoft Corporation. Licensed under the MIT License.
import { execFileSync } from 'child_process';
import { DockerSandboxProvider, isLinuxDockerDaemon } from '../src/sandbox';

jest.mock('child_process');
const command = execFileSync as jest.MockedFunction<typeof execFileSync>;

describe('Linux Docker capability', () => {
  beforeEach(() => jest.resetAllMocks());

  it.each(['linux', ' linux\r\n'])('accepts successful exact Linux output %p', value => {
    expect(isLinuxDockerDaemon(0, Buffer.from(value))).toBe(true);
  });

  it.each(['windows', '', 'Linux', 'LINUX', '{"OSType":"linux"}', 'linux extra'])(
    'rejects unsupported output %p', value => {
      expect(isLinuxDockerDaemon(0, Buffer.from(value))).toBe(false);
    },
  );

  it('rejects failed status and invalid UTF-8', () => {
    expect(isLinuxDockerDaemon(1, Buffer.from('linux'))).toBe(false);
    expect(isLinuxDockerDaemon(0, Buffer.from([0xff, ...Buffer.from('linux')]))).toBe(false);
  });

  it('uses constant argv without a shell', async () => {
    command.mockReturnValue(Buffer.from('linux\n'));
    expect(await new DockerSandboxProvider().isAvailable()).toBe(true);
    expect(command).toHaveBeenCalledWith('docker', ['info', '--format', '{{.OSType}}'], {
      stdio: 'pipe', timeout: 10_000, shell: false,
    });
  });

  it('rejects Windows daemon sessions before invoking docker run', async () => {
    command.mockReturnValue(Buffer.from('windows\n'));
    const provider = new DockerSandboxProvider();
    expect(await provider.isAvailable()).toBe(false);
    await expect(provider.createSession('agent')).rejects.toThrow('Linux Docker sandbox unavailable');
    expect(command.mock.calls.every(call => Array.isArray(call[1]) && call[1][0] === 'info')).toBe(true);
  });

  it('fails closed when the info command fails even with Linux stdout', async () => {
    command.mockImplementation(() => { throw Object.assign(new Error('daemon failure'), {
      status: 1, stdout: Buffer.from('linux'),
    }); });
    const provider = new DockerSandboxProvider();
    expect(await provider.isAvailable()).toBe(false);
    await expect(provider.createSession('agent')).rejects.toThrow('Linux Docker sandbox unavailable');
  });

  it('preserves Linux session isolation flags', async () => {
    command.mockReturnValueOnce(Buffer.from('linux\n')).mockReturnValueOnce(Buffer.from('container-id'));
    const session = await new DockerSandboxProvider().createSession('agent');
    expect(session.agentId).toBe('agent');
    const args = command.mock.calls[1][1] as string[];
    expect(args).toEqual(expect.arrayContaining([
      'run', '-d', '--cap-drop=ALL', '--security-opt=no-new-privileges',
      '--memory=512m', '--cpus=1', '--pids-limit=256', '--read-only', '--network=none',
    ]));
    expect(args.slice(-4)).toEqual(['python:3.11-slim', 'tail', '-f', '/dev/null']);
  });
});
