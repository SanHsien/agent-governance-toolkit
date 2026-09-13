# NOTICE

agent-governance-toolkit (SanHsien maintenance fork)
Copyright 2026 SanHsien

This project is derived from [`microsoft/agent-governance-toolkit`](https://github.com/microsoft/agent-governance-toolkit), originally licensed under the MIT License.

Original work:

- Project: Agent Governance Toolkit (AGT)
- Authors: Microsoft Corporation and Agent Governance Toolkit contributors
- License: MIT
- Upstream: https://github.com/microsoft/agent-governance-toolkit
- Documentation: https://microsoft.github.io/agent-governance-toolkit/

This repository keeps the original MIT license text in [`LICENSE`](LICENSE). The upstream third-party notice list remains in [`NOTICE`](NOTICE). Modifications, documentation, and future project-specific changes in this fork are also licensed under MIT unless otherwise noted.

## License Notes

The MIT License allows use, copying, modification, merging, publication, distribution, sublicensing, and commercial use, provided that the original copyright notice and permission notice are included in all copies or substantial portions of the software.

When redistributing this project or substantial parts of it:

- Keep [`LICENSE`](LICENSE) with the original MIT text.
- Keep attribution to `microsoft/agent-governance-toolkit`.
- Keep [`NOTICE`](NOTICE) when redistributing the corresponding third-party material.
- Add separate attribution for new third-party libraries when their licenses require it.

## Project Scope

This repository ships runtime governance for autonomous AI agents: deterministic policy enforcement, zero-trust identity, execution sandboxing, SRE, and audit. It is a maintenance fork, not a second official product site.

It does not include API keys, Azure credentials, production audit logs, or unpublished policy packs. Do not commit `.env` files or secrets.

Official packages (`agent-governance-toolkit` on PyPI, `@microsoft/agent-governance-sdk` on npm, `Microsoft.AgentGovernance` on NuGet, `agent-governance` on crates.io) are published by the upstream project, not by this fork.

## Credits

Agent Governance Toolkit belongs to the upstream project. Python packages, language SDKs, policy engine, examples, and product documentation in this tree come from `microsoft/agent-governance-toolkit` unless a file in `docs/fork/` or the SanHsien overlay documents otherwise.

This project is not affiliated with, endorsed by, or sponsored by Microsoft Corporation beyond the rights granted by the MIT License. Use of Microsoft trademarks in modified versions must not cause confusion or imply Microsoft sponsorship; see [`TRADEMARKS.md`](TRADEMARKS.md).

Do not commit secrets, API keys, cookies, OAuth credentials, or account data.
