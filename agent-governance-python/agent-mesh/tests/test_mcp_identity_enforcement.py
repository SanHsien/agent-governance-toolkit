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


# ---------------------------------------------------------------------------
# B1 — invoke_tool dispatches only for a verified DID, using verified data
# ---------------------------------------------------------------------------


class _Bridge:
    """Bridge stub answering per DID with real HandshakeResult objects."""

    def __init__(self) -> None:
        self.answers: Dict[str, Any] = {}
        self.verify_peer = AsyncMock(side_effect=self._answer)

    async def _answer(self, did: str, *args: Any, **kwargs: Any) -> Any:
        return self.answers.get(did, _denied(did, "unknown peer"))


def _server_with(
    identity: Any, registry: Any = None, min_trust_score: int = 300
) -> tuple[TrustGatedMCPServer, _Bridge]:
    bridge = _Bridge()
    server = TrustGatedMCPServer(
        identity,
        trust_bridge=bridge,
        min_trust_score=min_trust_score,
        identity_registry=registry,
    )
    return server, bridge


class TestB1InvokeToolRequiresVerifiedIdentity:
    @pytest.mark.asyncio
    async def test_unverified_did_with_self_reported_score_is_refused(
        self, identity: Any
    ) -> None:
        # Codex repro: server_unverified_invoke (success=True, trust_verified=True).
        server, bridge = _server_with(identity)
        handler = AsyncMock(return_value="sensitive")
        server.register_tool("protected", handler, require_human_sponsor=True)

        call = await server.invoke_tool(
            "protected", {}, "did:mesh:forged", caller_trust_score=1000
        )

        assert call.success is False
        assert call.trust_verified is False
        assert call.error and "not verified" in call.error.lower()
        handler.assert_not_awaited()
        assert server._verified_clients == {}

    @pytest.mark.asyncio
    async def test_refused_call_is_still_audited(self, identity: Any) -> None:
        server, _ = _server_with(identity)
        server.register_tool("t", _handler)
        await server.invoke_tool("t", {}, "did:mesh:forged", caller_trust_score=1000)
        assert server.get_audit_summary()["recentCalls"] == 1

    @pytest.mark.asyncio
    async def test_unknown_tool_does_not_leak_to_unverified_caller(
        self, identity: Any
    ) -> None:
        server, _ = _server_with(identity)
        call = await server.invoke_tool("nope", {}, "did:mesh:forged")
        assert call.error and "not verified" in call.error.lower()

    @pytest.mark.asyncio
    async def test_denied_verification_does_not_enable_dispatch(
        self, identity: Any
    ) -> None:
        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:bad"] = _denied("did:mesh:bad")
        handler = AsyncMock(return_value="x")
        server.register_tool("t", handler)
        assert await server.verify_client("did:mesh:bad") is False
        call = await server.invoke_tool("t", {}, "did:mesh:bad", caller_trust_score=1000)
        assert call.success is False and call.trust_verified is False
        handler.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_score_comes_from_verification_not_the_caller(
        self, identity: Any
    ) -> None:
        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:low"] = _ok("did:mesh:low", score=100)
        server.register_tool("t", _handler, min_trust_score=500)
        await server.verify_client("did:mesh:low")
        call = await server.invoke_tool("t", {}, "did:mesh:low", caller_trust_score=1000)
        assert call.success is False and call.trust_verified is False
        assert call.trust_score == 100  # the verified score, not the claimed one
        assert "Insufficient trust score" in (call.error or "")

    @pytest.mark.asyncio
    async def test_capabilities_come_from_verification_not_the_caller(
        self, identity: Any
    ) -> None:
        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:nocap"] = _ok("did:mesh:nocap", caps=["use:fs"])
        bridge.answers["did:mesh:cap"] = _ok("did:mesh:cap", caps=["use:sql"])
        handler = AsyncMock(return_value="rows")
        server.register_tool("sql", handler, required_capability="use:sql")
        await server.verify_client("did:mesh:nocap")
        await server.verify_client("did:mesh:cap")

        forged = await server.invoke_tool(
            "sql", {}, "did:mesh:nocap", caller_capabilities=["use:sql", "admin:*"],
            caller_trust_score=1000,
        )
        assert forged.success is False
        assert "Missing capability" in (forged.error or "")
        handler.assert_not_awaited()

        genuine = await server.invoke_tool("sql", {}, "did:mesh:cap")
        assert genuine.success is True and genuine.trust_verified is True
        assert genuine.capabilities_checked == ["use:sql"]

    @pytest.mark.asyncio
    async def test_bool_only_adapter_grants_identity_but_no_score_or_capabilities(
        self, identity: Any
    ) -> None:
        bridge = SimpleNamespace(verify_peer=AsyncMock(return_value=True))
        server = TrustGatedMCPServer(identity, trust_bridge=bridge)
        server.register_tool("scored", _handler, min_trust_score=1)
        server.register_tool("open", _handler, min_trust_score=0)
        assert await server.verify_client("did:mesh:b") is True
        refused = await server.invoke_tool("scored", {}, "did:mesh:b", caller_trust_score=999)
        assert refused.success is False
        allowed = await server.invoke_tool("open", {}, "did:mesh:b")
        assert allowed.success is True

    @pytest.mark.asyncio
    async def test_expired_verification_is_refused(self, identity: Any) -> None:
        from datetime import datetime, timedelta, timezone

        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:a"] = _ok("did:mesh:a")
        server.register_tool("t", _handler)
        await server.verify_client("did:mesh:a")
        server._verified_clients["did:mesh:a"] = datetime.now(timezone.utc) - timedelta(
            minutes=15
        )
        call = await server.invoke_tool("t", {}, "did:mesh:a")
        assert call.success is False and call.trust_verified is False

    @pytest.mark.asyncio
    async def test_failed_reverification_revokes_the_old_grant(self, identity: Any) -> None:
        from datetime import datetime, timedelta, timezone

        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:a"] = _ok("did:mesh:a")
        server.register_tool("t", _handler)
        await server.verify_client("did:mesh:a")
        server._verified_clients["did:mesh:a"] = datetime.now(timezone.utc) - timedelta(
            minutes=15
        )
        bridge.answers["did:mesh:a"] = _denied("did:mesh:a", "revoked")
        assert await server.verify_client("did:mesh:a") is False
        call = await server.invoke_tool("t", {}, "did:mesh:a")
        assert call.success is False

    @pytest.mark.asyncio
    async def test_cache_entry_without_a_verification_record_is_refused(
        self, identity: Any
    ) -> None:
        # A bare timestamp (no trusted score/capabilities behind it) is not a grant.
        from datetime import datetime, timezone

        server, bridge = _server_with(identity)
        server.register_tool("t", _handler, min_trust_score=0)
        server._verified_clients["did:mesh:ghost"] = datetime.now(timezone.utc)
        call = await server.invoke_tool("t", {}, "did:mesh:ghost")
        assert call.success is False and call.trust_verified is False

    @pytest.mark.asyncio
    async def test_replacing_the_bridge_invalidates_existing_grants(
        self, identity: Any
    ) -> None:
        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:a"] = _ok("did:mesh:a")
        server.register_tool("t", _handler)
        await server.verify_client("did:mesh:a")
        assert (await server.invoke_tool("t", {}, "did:mesh:a")).success is True

        server.trust_bridge = _Bridge()  # new trust configuration
        assert (await server.invoke_tool("t", {}, "did:mesh:a")).success is False
        server.trust_bridge = None
        assert (await server.invoke_tool("t", {}, "did:mesh:a")).success is False

    @pytest.mark.asyncio
    async def test_verification_stays_valid_across_calls_within_ttl(
        self, identity: Any
    ) -> None:
        server, bridge = _server_with(identity)
        bridge.answers["did:mesh:a"] = _ok("did:mesh:a")
        server.register_tool("t", _handler)
        await server.verify_client("did:mesh:a")
        for _ in range(3):
            assert (await server.invoke_tool("t", {}, "did:mesh:a")).success is True
        bridge.verify_peer.assert_awaited_once()  # invoke_tool never re-asks the bridge


class TestB1RequireHumanSponsorIsEnforced:
    @staticmethod
    def _registered(sponsor_verified: bool) -> tuple[AgentIdentity, IdentityRegistry]:
        peer = AgentIdentity.create(name="peer", sponsor="owner@test.com")
        peer.sponsor_verified = sponsor_verified
        registry = IdentityRegistry()
        registry.register(peer)
        return peer, registry

    @pytest.mark.asyncio
    async def test_sponsor_tool_refused_without_any_sponsor_evidence(
        self, identity: Any
    ) -> None:
        server, bridge = _server_with(identity)  # no identity_registry
        bridge.answers["did:mesh:a"] = _ok("did:mesh:a")
        handler = AsyncMock(return_value="x")
        server.register_tool("t", handler, require_human_sponsor=True)
        await server.verify_client("did:mesh:a")
        call = await server.invoke_tool("t", {}, "did:mesh:a", caller_trust_score=1000)
        assert call.success is False and call.trust_verified is False
        assert "sponsor" in (call.error or "").lower()
        handler.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sponsor_tool_refused_when_registry_says_unverified(
        self, identity: Any
    ) -> None:
        peer, registry = self._registered(sponsor_verified=False)
        did = str(peer.did)
        server, bridge = _server_with(identity, registry)
        bridge.answers[did] = _ok(did)
        server.register_tool("t", _handler, require_human_sponsor=True)
        await server.verify_client(did)
        call = await server.invoke_tool("t", {}, did)
        assert call.success is False and "sponsor" in (call.error or "").lower()

    @pytest.mark.asyncio
    async def test_sponsor_tool_allowed_when_registry_says_verified(
        self, identity: Any
    ) -> None:
        peer, registry = self._registered(sponsor_verified=True)
        did = str(peer.did)
        server, bridge = _server_with(identity, registry)
        bridge.answers[did] = _ok(did)
        server.register_tool("t", _handler, require_human_sponsor=True)
        await server.verify_client(did)
        call = await server.invoke_tool("t", {}, did)
        assert call.success is True and call.trust_verified is True

    @pytest.mark.asyncio
    async def test_tool_without_sponsor_requirement_ignores_sponsor_state(
        self, identity: Any
    ) -> None:
        peer, registry = self._registered(sponsor_verified=False)
        did = str(peer.did)
        server, bridge = _server_with(identity, registry)
        bridge.answers[did] = _ok(did)
        server.register_tool("t", _handler)
        await server.verify_client(did)
        assert (await server.invoke_tool("t", {}, did)).success is True
