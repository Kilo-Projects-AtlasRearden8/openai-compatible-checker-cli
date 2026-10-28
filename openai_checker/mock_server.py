"""Built-in mock OpenAI-compatible server.

Serves a tiny HTTP API that mirrors the OpenAI chat/completions and models
endpoints. Intended for local testing and demos -- no keys, no network, no
cloud accounts required.

Run directly::

    python -m openai_checker.mock_server [--port PORT] [--host HOST]

Endpoints:
  GET  /v1/models        -> list of available mock models
  POST /v1/chat/completions -> echo-style completion response
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Optional

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

MOCK_MODELS: List[Dict[str, str]] = [
    {"id": "mock-model", "object": "model"},
    {"id": "mock-chat-model", "object": "model"},
]


class _Handler(BaseHTTPRequestHandler):
    """Request handler for the mock server."""

    # Silence per-request log lines to keep demo output clean.
    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return

    def _send_json(self, status: int, payload: Dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/v1/models":
            self._send_json(200, {"object": "list", "data": MOCK_MODELS})
        else:
            self._send_json(404, {"error": {"message": "Not found", "type": "not_found"}})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path != "/v1/chat/completions":
            self._send_json(404, {"error": {"message": "Not found", "type": "not_found"}})
            return

        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": {"message": "Invalid JSON", "type": "invalid_request_error"}})
            return

        messages = payload.get("messages", [])
        if not isinstance(messages, list) or not messages:
            self._send_json(
                400,
                {"error": {"message": "messages is required", "type": "invalid_request_error"}},
            )
            return

        last_user = ""
        for message in reversed(messages):
            if isinstance(message, dict) and message.get("role") == "user":
                last_user = str(message.get("content", ""))
                break

        model = payload.get("model", "mock-model")
        reply = f"Mock reply to: {last_user}" if last_user else "Mock reply."

        self._send_json(
            200,
            {
                "id": "chatcmpl-mock",
                "object": "chat.completion",
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": reply},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": len(last_user.split()),
                    "completion_tokens": len(reply.split()),
                    "total_tokens": len(last_user.split()) + len(reply.split()),
                },
            },
        )


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Start the mock server on ``host``:``port`` (blocking)."""
    server = ThreadingHTTPServer((host, port), _Handler)
    print(f"Mock OpenAI-compatible server listening on http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server.")
    finally:
        server.server_close()


if __name__ == "__main__":  # pragma: no cover - manual use
    import argparse

    parser = argparse.ArgumentParser(
        description="Run a local mock OpenAI-compatible server."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind to.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind to.")
    args = parser.parse_args()
    run(host=args.host, port=args.port)
