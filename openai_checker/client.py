"""HTTP client for OpenAI-compatible endpoints.

Uses only the Python standard library (urllib) so the tool runs without
installing third-party packages. This keeps it local-first and beginner
friendly.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


class OpenAICompatibleError(Exception):
    """Raised when an OpenAI-compatible endpoint returns an error."""


@dataclass
class EndpointConfig:
    """Configuration for an OpenAI-compatible endpoint."""

    base_url: str
    timeout: float = 10.0
    model: Optional[str] = None


class OpenAICompatibleClient:
    """Minimal client for OpenAI-compatible chat/completions endpoints."""

    def __init__(self, config: EndpointConfig) -> None:
        self.config = config
        # Normalize the base URL so path joining is predictable.
        self.base_url = config.base_url.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data: Optional[bytes] = None
        headers: Dict[str, str] = {"Accept": "application/json"}

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(
                request, timeout=self.config.timeout
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            detail = self._extract_error_message(raw)
            raise OpenAICompatibleError(
                f"HTTP {exc.code} from {url}: {detail or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise OpenAICompatibleError(
                f"Unable to reach {url}: {exc.reason}"
            ) from exc

        if not raw:
            return {}

        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise OpenAICompatibleError(
                f"Invalid JSON response from {url}: {exc}"
            ) from exc

    @staticmethod
    def _extract_error_message(raw: bytes) -> str:
        try:
            payload = json.loads(raw.decode("utf-8"))
            error = payload.get("error", {})
            if isinstance(error, dict):
                return str(error.get("message", ""))
            return str(error)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return raw.decode("utf-8", errors="replace")[:200]

    def list_models(self) -> List[Dict[str, Any]]:
        """Return the list of models exposed by the endpoint."""
        payload = self._request("GET", "/v1/models")
        models = payload.get("data", [])
        if not isinstance(models, list):
            raise OpenAICompatibleError(
                "Unexpected /v1/models response: 'data' is not a list"
            )
        return models

    def chat_completion(
        self,
        messages: Iterable[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request and return the parsed response."""
        model_name = model or self.config.model
        if not model_name:
            raise OpenAICompatibleError(
                "No model specified. Pass --model or set a default model."
            )

        body: Dict[str, Any] = {
            "model": model_name,
            "messages": list(messages),
            "temperature": temperature,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens

        return self._request("POST", "/v1/chat/completions", body=body)

    def chat_message(self, message: str, **kwargs: Any) -> str:
        """Send a single user message and return the assistant's reply text."""
        response = self.chat_completion(
            messages=[{"role": "user", "content": message}], **kwargs
        )
        choices = response.get("choices", [])
        if not choices:
            raise OpenAICompatibleError("No choices returned in chat completion")
        first_choice = choices[0]
        message_obj = first_choice.get("message", {})
        content = message_obj.get("content", "")
        if not isinstance(content, str):
            content = str(content)
        return content
