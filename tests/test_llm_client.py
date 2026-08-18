import pytest
import requests
from pastapress.llm_client import LLMClient, LLMProcessingError
from tests.conftest import FakeResponse


def test_echo_roundtrip(mock_ollama_echo):
    client = LLMClient(host="http://test:11434", model="test-model")
    result = client.process_text("Hallo Welt.")
    assert result == "Hallo Welt."
    assert mock_ollama_echo == ["Hallo Welt."]


def test_whitespace_only_text_is_returned_unchanged(mock_ollama_echo):
    client = LLMClient(host="http://test:11434", model="test-model")
    assert client.process_text("   \n  ") == "   \n  "
    # Nothing must be sent to the LLM for whitespace-only input.
    assert mock_ollama_echo == []


def test_retry_then_success(monkeypatch):
    client = LLMClient(host="http://test:11434", model="test-model")
    calls = {"n": 0}

    def flaky_post(url, json=None, timeout=None):
        calls["n"] += 1
        if calls["n"] < 3:
            raise requests.exceptions.ConnectionError("boom")
        return FakeResponse({"message": {"content": "ok"}})

    monkeypatch.setattr("pastapress.llm_client.requests.post", flaky_post)
    monkeypatch.setattr("pastapress.llm_client.time.sleep", lambda s: None)

    assert client.process_text("test", retries=3) == "ok"
    assert calls["n"] == 3


def test_raises_after_max_retries(mock_ollama_down):
    client = LLMClient(host="http://test:11434", model="test-model")
    with pytest.raises(LLMProcessingError):
        client.process_text("test", retries=3)


def test_empty_llm_response_triggers_retry(monkeypatch):
    client = LLMClient(host="http://test:11434", model="test-model")
    responses = [
        FakeResponse({"message": {"content": "   "}}),
        FakeResponse({"message": {"content": "gefuellt"}}),
    ]

    def post(url, json=None, timeout=None):
        return responses.pop(0)

    monkeypatch.setattr("pastapress.llm_client.requests.post", post)
    monkeypatch.setattr("pastapress.llm_client.time.sleep", lambda s: None)

    assert client.process_text("test") == "gefuellt"


def test_unexpected_response_format_raises(monkeypatch):
    client = LLMClient(host="http://test:11434", model="test-model")
    monkeypatch.setattr("pastapress.llm_client.requests.post",
                        lambda url, json=None, timeout=None: FakeResponse({"error": "kaputt"}))
    monkeypatch.setattr("pastapress.llm_client.time.sleep", lambda s: None)

    with pytest.raises(LLMProcessingError):
        client.process_text("test", retries=2)


def test_host_trailing_slash_is_normalized():
    client = LLMClient(host="http://test:11434/", model="m")
    assert client.api_url == "http://test:11434/api/chat"
