"""Command-line interface for the OpenAI-compatible endpoint checker."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .client import EndpointConfig, OpenAICompatibleClient, OpenAICompatibleError
from .mock_server import DEFAULT_HOST, DEFAULT_PORT, run as run_mock_server
from .tokens import count_tokens, estimate_cost


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openai-checker",
        description=(
            "Smoke-test OpenAI-compatible endpoints (Ollama, LM Studio, "
            "Kilo Gateway) locally: list models, run a chat completion, "
            "and count tokens. No API keys or cloud accounts needed."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s 0.1.0"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # Shared endpoint options
    def add_endpoint_args(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--url",
            default="http://127.0.0.1:11434",
            help="Base URL of the OpenAI-compatible endpoint "
            "(default: http://127.0.0.1:11434, typical for Ollama).",
        )
        p.add_argument(
            "--model",
            default=None,
            help="Model name to use (required for chat unless --default-model is set).",
        )
        p.add_argument(
            "--timeout",
            type=float,
            default=10.0,
            help="Request timeout in seconds (default: 10).",
        )

    # models command
    p_models = sub.add_parser("models", help="List models exposed by the endpoint.")
    add_endpoint_args(p_models)

    # chat command
    p_chat = sub.add_parser("chat", help="Send a chat completion to the endpoint.")
    add_endpoint_args(p_chat)
    p_chat.add_argument(
        "--message",
        "-m",
        default="Hello!",
        help="Message to send (default: 'Hello!').",
    )
    p_chat.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7).",
    )
    p_chat.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Maximum tokens to generate.",
    )

    # token-count command
    p_tokens = sub.add_parser(
        "token-count", help="Count tokens in text (approximate without tiktoken)."
    )
    p_tokens.add_argument(
        "--text",
        "-t",
        default="",
        help="Text to count tokens for.",
    )
    p_tokens.add_argument(
        "--file",
        "-f",
        default=None,
        help="Read text from a file instead of --text.",
    )
    p_tokens.add_argument(
        "--model",
        default=None,
        help="Model name for tiktoken (falls back to cl100k_base).",
    )
    p_tokens.add_argument(
        "--price-per-1k",
        type=float,
        default=0.0015,
        help="Price per 1,000 input tokens for cost estimate (default: 0.0015).",
    )

    # mock-server command
    p_mock = sub.add_parser(
        "mock-server", help="Run a local mock OpenAI-compatible server for testing."
    )
    p_mock.add_argument(
        "--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})."
    )
    p_mock.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind to (default: {DEFAULT_PORT}).",
    )

    return parser


def cmd_models(args: argparse.Namespace) -> int:
    config = EndpointConfig(base_url=args.url, model=args.model, timeout=args.timeout)
    client = OpenAICompatibleClient(config)
    try:
        models = client.list_models()
    except OpenAICompatibleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not models:
        print("No models found.")
        return 0

    print("Models:")
    for entry in models:
        model_id = entry.get("id", "unknown") if isinstance(entry, dict) else str(entry)
        print(f"  - {model_id}")
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    config = EndpointConfig(base_url=args.url, model=args.model, timeout=args.timeout)
    client = OpenAICompatibleClient(config)
    try:
        reply = client.chat_message(
            args.message,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    except OpenAICompatibleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(reply)
    return 0


def cmd_token_count(args: argparse.Namespace) -> int:
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"Error reading {args.file}: {exc}", file=sys.stderr)
            return 1
    else:
        text = args.text

    tokens = count_tokens(text, model=args.model)
    cost = estimate_cost(tokens, price_per_1k=args.price_per_1k)

    print(f"Tokens: {tokens}")
    print(f"Characters: {len(text)}")
    print(f"Estimated cost (@${args.price_per_1k:.4f}/1K tokens): ${cost:.6f}")
    return 0


def cmd_mock_server(args: argparse.Namespace) -> int:
    run_mock_server(host=args.host, port=args.port)
    return 0


_COMMAND_HANDLERS = {
    "models": cmd_models,
    "chat": cmd_chat,
    "token-count": cmd_token_count,
    "mock-server": cmd_mock_server,
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.print_help(sys.stderr)
        return 2
    return handler(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
