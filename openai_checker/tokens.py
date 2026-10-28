"""Token counting helpers.

Tries to use ``tiktoken`` when available for accurate OpenAI-style token
counts, and falls back to a simple, clearly-labeled approximation when it is
not installed. This keeps the tool usable offline without any third-party
dependencies while still being accurate when ``tiktoken`` is present.
"""

from __future__ import annotations

import re

try:  # pragma: no cover - optional dependency
    import tiktoken  # type: ignore

    _TIKTOKEN_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None  # type: ignore
    _TIKTOKEN_AVAILABLE = False


# A rough heuristic: ~4 characters per token for English text.
_CHARS_PER_TOKEN = 4.0

# Tokenizes on whitespace and punctuation boundaries for the fallback estimate.
_WORD_RE = re.compile(r"\S+|\s+")


def count_tokens(text: str, model: Optional[str] = None) -> int:
    """Count tokens in ``text``.

    Uses ``tiktoken`` when available (matching the given ``model`` when
    possible), otherwise returns a conservative approximation. The return
    value is always an integer >= 0.
    """
    if not text:
        return 0

    if _TIKTOKEN_AVAILABLE:
        try:
            encoding = _get_encoding(model)
            return len(encoding.encode(text))
        except Exception:
            # Fall through to the heuristic if anything goes wrong.
            pass

    return _heuristic_count(text)


def _get_encoding(model: Optional[str]):
    """Return a tiktoken encoding for the given model name."""
    if tiktoken is None:  # pragma: no cover - guarded by caller
        raise ImportError("tiktoken is not installed")
    if model:
        try:
            return tiktoken.encoding_for_model(model)
        except KeyError:
            pass
    return tiktoken.get_encoding("cl100k_base")


def _heuristic_count(text: str) -> int:
    """Approximate token count: roughly 4 characters per token."""
    return max(1, int(len(text) / _CHARS_PER_TOKEN))


def estimate_cost(tokens: int, price_per_1k: float = 0.0015) -> float:
    """Estimate cost in dollars for a token count (input pricing)."""
    if tokens < 0:
        tokens = 0
    return (tokens / 1000.0) * price_per_1k
