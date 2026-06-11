"""llama.cpp slot-affinity fields must never reach cloud providers (#3793).

_apply_local_cache_affinity adds session_id + cache_prompt to outgoing
payloads for KV-cache slot affinity (#2927). The old gate treated any unknown
OpenAI-compatible host as self-hosted, so strict cloud APIs added as custom
endpoints (Mistral at api.mistral.ai) received the extra fields and rejected
every request with 422 extra_forbidden. Self-hosted now also requires the
endpoint to resolve as local: loopback/private/tailscale host, or endpoint
kind explicitly configured as "local".
"""
import pytest

import src.llm_core as llm_core
import src.model_context as model_context


def _affinity_fields(url, monkeypatch, kind=None):
    monkeypatch.setattr(model_context, "_configured_endpoint_kind", lambda _u: kind)
    payload = {}
    llm_core._apply_local_cache_affinity(payload, url, "sess-123")
    return payload


def test_mistral_cloud_api_gets_no_affinity_fields(monkeypatch):
    # The #3793 repro: Mistral rejects unknown body fields with 422.
    payload = _affinity_fields("https://api.mistral.ai/v1", monkeypatch)
    assert payload == {}


def test_openai_api_gets_no_affinity_fields(monkeypatch):
    payload = _affinity_fields("https://api.openai.com/v1", monkeypatch)
    assert payload == {}


def test_unknown_public_host_gets_no_affinity_fields(monkeypatch):
    # Any strict cloud provider added as a custom endpoint, not just Mistral.
    payload = _affinity_fields("https://llm.example-cloud.com/v1", monkeypatch)
    assert payload == {}


def test_localhost_server_gets_affinity_fields(monkeypatch):
    payload = _affinity_fields("http://localhost:8080/v1", monkeypatch)
    assert payload == {"session_id": "sess-123", "cache_prompt": True}


def test_private_lan_server_gets_affinity_fields(monkeypatch):
    payload = _affinity_fields("http://192.168.1.50:8000/v1", monkeypatch)
    assert payload == {"session_id": "sess-123", "cache_prompt": True}


def test_public_host_with_local_kind_override_gets_affinity_fields(monkeypatch):
    # Escape hatch: a self-hosted llama.cpp exposed via a tunnel keeps the
    # slot-affinity hint when its endpoint kind is configured as "local".
    payload = _affinity_fields("https://my-llama.example.com/v1", monkeypatch, kind="local")
    assert payload == {"session_id": "sess-123", "cache_prompt": True}


def test_no_session_id_is_a_noop(monkeypatch):
    monkeypatch.setattr(model_context, "_configured_endpoint_kind", lambda _u: None)
    payload = {}
    llm_core._apply_local_cache_affinity(payload, "http://localhost:8080/v1", None)
    assert payload == {}
