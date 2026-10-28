# STATUS

openai-compatible-checker-cli — local-first smoke test for OpenAI-compatible
endpoints (Ollama, LM Studio, Kilo Gateway).

## What was built

A dependency-free Python CLI (standard library only) that smoke-tests
OpenAI-compatible HTTP endpoints:

* `models` — lists models exposed by an endpoint (`GET /v1/models`)
* `chat` — sends a chat completion and prints the assistant's reply
  (`POST /v1/chat/completions`)
* `token-count` — counts tokens in text (exact with `tiktoken`, heuristic
  approximation without it) plus a cost estimate
* `mock-server` — built-in mock OpenAI-compatible server for offline testing
  and demos (no keys, no network, no cloud)

Package layout:

```
openai_checker/        # package
  __init__.py          # version
  __main__.py          # CLI entry point (argparse subcommands)
  client.py            # stdlib urllib client for models/chat
  tokens.py            # token counting (tiktoken optional, heuristic fallback)
  mock_server.py       # built-in mock HTTP server
  py.typed             # PEP 561 marker
tests/                 # stdlib pytest tests (mock-server based)
  test_tokens.py
  test_client.py
pyproject.toml         # packaging + pytest config
README.md              # user guide + Asdale Dynamics, LLC credit
LICENSE                # MIT, Copyright (c) 2026 Asdale Dynamics, LLC
STATUS.md              # this file
```

## How to run

```bash
# From the project folder (no install required):
python3 -m openai_checker --help

# List models (default URL targets Ollama at 127.0.0.1:11434):
python3 -m openai_checker models --url http://127.0.0.1:11434

# Chat completion:
python3 -m openai_checker chat --url http://127.0.0.1:11434 \
  --model llama3 --message "Explain local AI like I'm new to it."

# Count tokens:
python3 -m openai_checker token-count --text "Hello world" \
  --model gpt-3.5-turbo

# Built-in mock server (offline testing):
python3 -m openai_checker mock-server --port 8765
# then, in another terminal:
python3 -m openai_checker models --url http://127.0.0.1:8765

# Install for the `openai-checker` command:
pip install .

# Run tests (stdlib + built-in mock server, no keys/network/cloud):
python3 -m pytest
```

## Verification results

* `python3 -m openai_checker --help` — runs, lists all subcommands.
* `python3 -m openai_checker models --help` / `chat --help` — run correctly.
* `python3 -m pytest` — **8 passed** (test_tokens + test_client against the
  built-in mock server).
* End-to-end against the mock server on port 8999:
  * `models` returned `mock-model` and `mock-chat-model`.
  * `chat --message "hello friend"` returned `Mock reply to: hello friend`.
* `token-count` works for inline text and errors cleanly on a missing file.

No secrets, API keys, or personal data in any file. No `.github/workflows`
added.

## Known gaps

* Token counting falls back to a character-based heuristic (~4 chars per
  token) when `tiktoken` is not installed; install `tiktoken` for exact
  OpenAI-style counts.
* Only JSON `application/x-www-form-urlencoded`-style chat completions are
  tested; streaming (`stream: true`) is not implemented.
* Default `--url` assumes Ollama (`127.0.0.1:11434`); LM Studio and Kilo
  Gateway require an explicit `--url`.
* No authentication header support (intended: local-first, no keys).

## Credits

Built and published by **Asdale Dynamics, LLC** (Indiana, formed October
2026). MIT License — Copyright (c) 2026 Asdale Dynamics, LLC.
