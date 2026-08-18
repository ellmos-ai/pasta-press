import pytest


class FakeResponse:
    """Minimal stand-in for requests.Response as used by LLMClient."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


@pytest.fixture
def mock_ollama_echo(monkeypatch):
    """
    Patches requests.post at the llm_client level so the "LLM" echoes the
    user message back — exactly the way a perfectly obedient model would.
    This exercises the real response-handling path including .strip().
    Returns a list that records every user-message content sent to the LLM.
    """
    sent = []

    def fake_post(url, json=None, timeout=None):
        user_content = json["messages"][-1]["content"]
        sent.append(user_content)
        return FakeResponse({"message": {"content": user_content}})

    monkeypatch.setattr("pastapress.llm_client.requests.post", fake_post)
    return sent


@pytest.fixture
def mock_ollama_down(monkeypatch):
    """Patches requests.post to always fail, and removes retry sleeps."""
    import requests

    def fake_post(url, json=None, timeout=None):
        raise requests.exceptions.ConnectionError("Ollama unreachable (mocked)")

    monkeypatch.setattr("pastapress.llm_client.requests.post", fake_post)
    monkeypatch.setattr("pastapress.llm_client.time.sleep", lambda s: None)
