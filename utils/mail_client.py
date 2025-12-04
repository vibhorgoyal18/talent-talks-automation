from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class GmailClientError(RuntimeError):
    """Raised for HTTP or data issues when calling Gmail API."""


@dataclass
class GmailMessage:
    id: str
    thread_id: Optional[str]
    snippet: Optional[str]
    payload: Dict[str, Any]


class GmailClient:
    """Thin wrapper over Gmail REST API using an API key."""

    BASE_URL = "https://gmail.googleapis.com/gmail/v1"

    def __init__(self, api_key: str, user_id: str = "me", timeout: int = 10) -> None:
        if not api_key:
            raise ValueError("Gmail API key must be provided")
        self.api_key = api_key
        self.user_id = user_id
        self.timeout = timeout

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        params.setdefault("key", self.api_key)
        url = f"{self.BASE_URL}/users/{self.user_id}{path}"
        response = requests.get(url, params=params, timeout=self.timeout)
        if response.status_code != 200:
            raise GmailClientError(f"Gmail API error {response.status_code}: {response.text}")
        return response.json()

    def list_messages(self, query: str = "", max_results: int = 5) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"maxResults": max_results}
        if query:
            params["q"] = query
        data = self._request("/messages", params)
        return data.get("messages", [])

    def get_message(self, message_id: str, fmt: str = "full") -> GmailMessage:
        data = self._request(f"/messages/{message_id}", {"format": fmt})
        return GmailMessage(
            id=data.get("id", message_id),
            thread_id=data.get("threadId"),
            snippet=data.get("snippet"),
            payload=data.get("payload", {}),
        )

    def fetch_latest(self, query: str = "") -> Optional[GmailMessage]:
        messages = self.list_messages(query=query, max_results=1)
        if not messages:
            return None
        message_id = messages[0]["id"]
        return self.get_message(message_id)
