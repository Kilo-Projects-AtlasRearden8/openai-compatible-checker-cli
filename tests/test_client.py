"""Integration-style tests using the built-in mock server (stdlib only)."""

import json
import threading
import urllib.request

import pytest

from openai_checker.client import (
    EndpointConfig,
    OpenAICompatibleClient,
    OpenAICompatibleError,
)
from openai_checker.mock_server import DEFAULT_PORT, run as run_mock_server


@pytest.fixture(scope="module")
def mock_server_port():
    port = DEFAULT_PORT
    server_thread = threading.Thread(
        target=run_mock_server, kwargs={"host": "127.0.0.1", "port": port}, daemon=True
    )
    server_thread.start()
    yield port


def _base_url(port):
    return f"http://127.0.0.1:{port}"


def test_list_models(mock_server_port):
    config = EndpointConfig(base_url=_base_url(mock_server_port), timeout=5.0)
    client = OpenAICompatibleClient(config)
    models = client.list_models()
    assert isinstance(models, list)
    assert len(models) >= 1
    ids = {entry.get("id") for entry in models}
    assert "mock-model" in ids


def test_chat_completion(mock_server_port):
    config = EndpointConfig(
        base_url=_base_url(mock_server_port), model="mock-model", timeout=5.0
    )
    client = OpenAICompatibleClient(config)
    reply = client.chat_message("Hello from the test suite")
    assert isinstance(reply, str)
    assert "Mock reply to:" in reply


def test_chat_missing_model_raises(mock_server_port):
    config = EndpointConfig(base_url=_base_url(mock_server_port), timeout=5.0)
    client = OpenAICompatibleClient(config)
    with pytest.raises(OpenAICompatibleError):
        client.chat_message("Hello")


def test_raw_http_endpoint_responds(mock_server_port):
    """Exercise the mock server over raw HTTP to confirm the wire format."""
    url = f"{_base_url(mock_server_port)}/v1/chat/completions"
    body = json.dumps(
        {"model": "mock-model", "messages": [{"role": "user", "content": "ping"}]}
    ).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=5.0) as response:
        payload = json.loads(response.read().decode("utf-8"))
    assert payload["object"] == "chat.completion"
    assert payload["choices"][0]["message"]["role"] == "assistant"
