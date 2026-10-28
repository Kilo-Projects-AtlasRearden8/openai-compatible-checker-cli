# openai-compatible-checker-cli

A small, local-first Python CLI that smoke-tests OpenAI-compatible HTTP
endpoints -- Ollama, LM Studio, Kilo Gateway, and anything else that speaks
the OpenAI chat/completions API. It can list models, run a chat completion,
and count tokens. No API keys and no cloud accounts required.

Built and published by **Asdale Dynamics, LLC** (Indiana, formed October 2026).
Part of the LLC's open-source tooling for beginner-friendly AI education and
practical local-first utilities.

## Who this is for

This tool is for anyone running local LLMs who wants a quick way to confirm
an endpoint is reachable and responding -- no sign-up, no credit card, no
cloud. It's especially suited to:

* People learning local AI (Ollama, LM Studio) for the first time.
* Developers self-hosting the Kilo Gateway or other OpenAI-compatible proxies.
* Anyone who wants a dependency-free, offline-capable smoke test.

It was written with the beginner-friendly spirit of Asdale Dynamics' guides:
plain English, step by step, never condescending.

## Features

* `models` -- list the models an endpoint exposes (`GET /v1/models`)
* `chat` -- send a chat completion and print the assistant's reply
  (`POST /v1/chat/completions`)
* `token-count` -- count tokens in text (accurate with `tiktoken`, approximate
  without it) plus a cost estimate
* `mock-server` -- run a built-in mock OpenAI-compatible server for offline
  testing and demos

## Install

```bash
# From this folder, using the standard library only (no install needed):
python -m openai_checker --help

# Or install the package (provides the `openai-checker` command):
pip install .
openai-checker --help
```

No third-party packages are required. If you install `tiktoken`, token
counting becomes exact for OpenAI-style models; otherwise a simple, clearly
labeled approximation is used.

## Quick start

### 1. List models

Point it at a local endpoint (Ollama's default port is 11434):

```bash
python -m openai_checker models --url http://127.0.0.1:11434
```

### 2. Run a chat completion

```bash
python -m openai_checker chat \
  --url http://127.0.0.1:11434 \
  --model llama3 \
  --message "Explain local AI like I'm new to it."
```

### 3. Count tokens

```bash
python -m openai_checker token-count \
  --text "This is some text to count." \
  --model gpt-3.5-turbo
```

Or read from a file:

```bash
python -m openai_checker token-count --file notes.txt
```

### 4. Use the built-in mock server (offline testing)

```bash
python -m openai_checker mock-server --port 8765
```

In another terminal, point the checker at it:

```bash
python -m openai_checker models --url http://127.0.0.1:8765
python -m openai_checker chat --url http://127.0.0.1:8765 --model mock-model --message "hi"
```

## Run the tests

```bash
python -m pytest
```

Tests use only the standard library plus the built-in mock server -- no keys,
no network, no cloud.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is an Indiana company (formed October 2026) founded by
Dylan Asdale, a registered nurse turned AI author. Through *The Massive AI
Manual* and the hub site dylanasdale.github.io, the LLC explains AI "like a
friend would": plain English, step by step, never condescending.

The LLC focuses on beginner-friendly AI education, books and guides, and
practical open-source tools -- including local-LLM utilities like this one --
that it can publish or sell. Everything here is local-first, tested, and free
of secrets or personal data.
