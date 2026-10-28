"""Unit tests for tokens.py (stdlib-only, runs offline)."""

import pytest

from openai_checker.tokens import count_tokens, estimate_cost


def test_empty_text_returns_zero():
    assert count_tokens("") == 0


def test_counts_nonempty_text():
    assert count_tokens("Hello world") >= 1


def test_heuristic_roughly_chars_per_token():
    text = "A" * 100
    assert count_tokens(text) == 25  # 100 / 4


def test_estimate_cost_non_negative():
    assert estimate_cost(0) == 0.0
    assert estimate_cost(1000, price_per_1k=0.0015) == 0.0015
    assert estimate_cost(-5) == 0.0
