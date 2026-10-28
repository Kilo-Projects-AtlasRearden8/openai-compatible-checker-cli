"""OpenAI-compatible endpoint checker.

A small, local-first Python CLI that smoke-tests OpenAI-compatible HTTP
endpoints such as Ollama, LM Studio, and the Kilo Gateway. It can list
models, send a chat completion, and count tokens -- no API keys or cloud
accounts required.
"""

__version__ = "0.1.0"
