# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Regression tests for MCP identity-enforcement gaps found by independent review.

Fork-only (see docs/fork/DECISIONS.md, 2026-11-11). Each class pins one
finding and uses the real ``HandshakeResult`` model, because a bool mock is
exactly what hid the original interface mismatch:

* B1  ``invoke_tool`` must not trust caller-supplied identity claims.
* B2  ``HandshakeResult(verified=False)`` is truthy and must not pass.
* B3  a bridge denial must not fall through to self-reported card scores.
* B4  a failed or changed re-connect must revoke earlier connected state.
* B5  a configured bridge is detected with ``is not None``, not truthiness.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from agentmesh.identity import AgentIdentity
from agentmesh.identity.agent_id import IdentityRegistry
from agentmesh.integrations.mcp import TrustGatedMCPClient, TrustGatedMCPServer
from agentmesh.trust.bridge import TrustBridge
from agentmesh.trust.handshake import HandshakeResult

SERVER_URL = "https://mcp.example.com"


def _ok(
    did: str, score: int = 800, caps: Optional[List[str]] = None
) -> HandshakeResult:
    return HandshakeResult.success(
        peer_did=did, trust_score=score, capabilities=caps or []
    )


def _denied(did: str, reason: str = "invalid signature") -> HandshakeResult:
    return HandshakeResult.failure(peer_did=did, reason=reason)


def _bridge(result: Any = None, side_effect: Any = None) -> SimpleNamespace:
    return SimpleNamespace(
        verify_peer=AsyncMock(return_value=result, side_effect=side_effect)
    )


class _FalseyBridge:
    """A configured bridge whose truth value is False (e.g. an empty registry)."""

    def __init__(self, result: Any) -> None:
        self.verify_peer = AsyncMock(return_value=result)

    def __bool__(self) -> bool:
        return False


@pytest.fixture()
def identity() -> AgentIdentity:
    return AgentIdentity.create(name="mcp-peer", sponsor="admin@test.com")


async def _handler(**kwargs: Any) -> Dict[str, Any]:
    return {"ran": True}


# ---------------------------------------------------------------------------
# Sanity: the premise of B2 is a property of the real model.
# ---------------------------------------------------------------------------


def test_rejected_handshake_result_is_truthy() -> None:
    assert _denied("did:mesh:x").verified is False
    assert bool(_denied("did:mesh:x")) is True


# ---------------------------------------------------------------------------
# B2 — verify_peer() returns HandshakeResult; judge `.verified is True`
# ---------------------------------------------------------------------------


class TestB2HandshakeResultContract:
    @pytest.mark.asyncio
    async def test_server_rejects_failed_handshake_result(self, identity: Any) -> None:
        server = TrustGatedMCPServer(identity, trust_bridge=_bridge(_denied("did:mesh:bad")))
        assert await server.verify_client("did:mesh:bad") is False
        assert "did:mesh:bad" not in server._verified_clients

    @pytest.mark.asyncio
    async def test_server_accepts_verified_handshake_result(self, identity: Any) -> None:
        server = TrustGatedMCPServer(identity, trust_bridge=_bridge(_ok("did:mesh:good")))
        assert await server.verify_client("did:mesh:good") is True
        assert "did:mesh:good" in server._verified_clients

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "unexpected",
        ["yes", 1, {"verified": True}, object(), MagicMock(), None],
        ids=["str", "int", "dict", "object", "magicmock", "none"],
    )
    async def test_server_rejects_unexpected_return_types(
        self, identity: Any, unexpected: Any
    ) -> None:
        server = TrustGatedMCPServer(identity, trust_bridge=_bridge(unexpected))
        assert await server.verify_client("did:mesh:odd") is False
        assert "did:mesh:odd" not in server._verified_clients

    @pytest.mark.asyncio
    async def test_server_rejects_result_for_a_different_did(self, identity: Any) -> None:
        # A verified result for another peer must not authenticate this DID.
        server = TrustGatedMCPServer(identity, trust_bridge=_bridge(_ok("did:mesh:other")))
        assert await server.verify_client("did:mesh:asked") is False

    @pytest.mark.asyncio
    async def test_server_with_real_trust_bridge_rejects_unknown_did(
        self, identity: Any
    ) -> None:
        bridge = TrustBridge(
            agent_did=str(identity.did), identity=identity, registry=IdentityRegistry()
        )
        server = TrustGatedMCPServer(identity, trust_bridge=bridge)
        assert await server.verify_client("did:mesh:not-registered") is False
        assert "did:mesh:not-registered" not in server._verified_clients

    @pytest.mark.asyncio
    async def test_client_rejects_failed_handshake_result(self, identity: Any) -> None:
        client = TrustGatedMCPClient(identity, _bridge(_denied("did:mesh:srv")))
        client._discover_server_did = AsyncMock(return_value="did:mesh:srv")
        assert await client.connect(SERVER_URL) is False
        assert SERVER_URL not in client._connected_servers

    @pytest.mark.asyncio
    async def test_client_accepts_verified_handshake_result(self, identity: Any) -> None:
        client = TrustGatedMCPClient(identity, _bridge(_ok("did:mesh:srv")))
        client._discover_server_did = AsyncMock(return_value="did:mesh:srv")
        assert await client.connect(SERVER_URL) is True
        assert SERVER_URL in client._connected_servers

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "unexpected",
        ["yes", 1, object(), MagicMock(), None],
        ids=["str", "int", "object", "magicmock", "none"],
    )
    async def test_client_rejects_unexpected_return_types(
        self, identity: Any, unexpected: Any
    ) -> None:
        client = TrustGatedMCPClient(identity, _bridge(unexpected))
        client._discover_server_did = AsyncMock(return_value="did:mesh:srv")
        assert await client.connect(SERVER_URL) is False
        assert SERVER_URL not in client._connected_servers

    @pytest.mark.asyncio
    async def test_client_rejects_result_for_a_different_did(self, identity: Any) -> None:
        client = TrustGatedMCPClient(identity, _bridge(_ok("did:mesh:other")))
        client._discover_server_did = AsyncMock(return_value="did:mesh:srv")
        assert await client.connect(SERVER_URL) is False


# ---------------------------------------------------------------------------
# B3 — a bridge denial is final; no card fallback
# ---------------------------------------------------------------------------


class TestB3NoCardFallbackAfterBridgeDenial:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("denial", [False, "denied-result"], ids=["bool", "handshake"])
    async def test_denied_by_bridge_is_not_rescued_by_high_card_score(
        self, identity: Any, denial: Any
    ) -> None:
        result = _denied("did:mesh:forged") if denial == "denied-result" else denial
        bridge = _bridge(result)
        server = TrustGatedMCPServer(identity, trust_bridge=bridge)
        card = SimpleNamespace(trust_score=1000)
        assert await server.verify_client("did:mesh:forged", card) is False
        bridge.verify_peer.assert_awaited_once_with("did:mesh:forged")
        assert "did:mesh:forged" not in server._verified_clients

    @pytest.mark.asyncio
    async def test_bridge_error_is_not_rescued_by_card(self, identity: Any) -> None:
        server = TrustGatedMCPServer(
            identity, trust_bridge=_bridge(side_effect=ConnectionError("down"))
        )
        assert await server.verify_client("did:mesh:x", SimpleNamespace(trust_score=1000)) is False

    @pytest.mark.asyncio
    async def test_unexpected_bridge_type_is_not_rescued_by_card(self, identity: Any) -> None:
        server = TrustGatedMCPServer(identity, trust_bridge=_bridge("maybe"))
        assert await server.verify_client("did:mesh:x", SimpleNamespace(trust_score=1000)) is False

    @pytest.mark.asyncio
    async def test_no_bridge_self_reported_card_score_is_not_identity(
        self, identity: Any
    ) -> None:
        # Without a bridge there is no trust anchor: a card's own trust_score
        # proves nothing (no signature, issuer, DID binding or expiry check).
        server = TrustGatedMCPServer(identity)
        assert await server.verify_client("did:mesh:x", SimpleNamespace(trust_score=1000)) is False
        assert "did:mesh:x" not in server._verified_clients


# ---------------------------------------------------------------------------
# B5 — bridge presence is `is not None`
# ---------------------------------------------------------------------------


class TestB5BridgePresenceIsNotTruthiness:
    @pytest.mark.asyncio
    async def test_server_consults_falsey_bridge_and_honours_denial(
        self, identity: Any
    ) -> None:
        bridge = _FalseyBridge(_denied("did:mesh:x"))
        server = TrustGatedMCPServer(identity, trust_bridge=bridge)
        card = SimpleNamespace(trust_score=1000)
        assert await server.verify_client("did:mesh:x", card) is False
        bridge.verify_peer.assert_awaited_once_with("did:mesh:x")

    @pytest.mark.asyncio
    async def test_server_consults_falsey_bridge_and_honours_approval(
        self, identity: Any
    ) -> None:
        bridge = _FalseyBridge(_ok("did:mesh:x"))
        server = TrustGatedMCPServer(identity, trust_bridge=bridge)
        assert await server.verify_client("did:mesh:x") is True
        bridge.verify_peer.assert_awaited_once_with("did:mesh:x")

    @pytest.mark.asyncio
    async def test_client_does_not_treat_falsey_bridge_as_absent(self, identity: Any) -> None:
        # Falsey bridge + undiscoverable DID: must fail closed, not connect.
        client = TrustGatedMCPClient(identity, _FalseyBridge(_ok("did:mesh:srv")))
        assert await client.connect(SERVER_URL) is False
        assert SERVER_URL not in client._connected_servers

    @pytest.mark.asyncio
    async def test_client_falsey_bridge_denial_is_honoured(self, identity: Any) -> None:
        bridge = _FalseyBridge(_denied("did:mesh:srv"))
        client = TrustGatedMCPClient(identity, bridge)
        client._discover_server_did = AsyncMock(return_value="did:mesh:srv")
        assert await client.connect(SERVER_URL) is False
        bridge.verify_peer.assert_awaited_once_with("did:mesh:srv")

    @pytest.mark.asyncio
    async def test_client_without_bridge_still_connects_unverified(
        self, identity: Any
    ) -> None:
        # Only an explicit None enters the (documented) unverified mode.
        client = TrustGatedMCPClient(identity, None)
        assert await client.connect(SERVER_URL) is True
