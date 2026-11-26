"""HTTP client for the Knowledge service."""

from typing import Any

import requests


class KnowledgeClient:
    """Thin wrapper over the Knowledge REST API."""

    def __init__(self, base_url: str, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self._session = session or requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def add_reading(self, reading: dict[str, Any]) -> None:
        """Append a sensor reading to the short-term memory."""
        self._session.post(self._url("/sensors"), json=reading)

    def get_short_term(self) -> list[dict[str, Any]]:
        """Return the readings in the short-term memory, oldest first."""
        readings: list[dict[str, Any]] = self._session.get(
            self._url("/short-term")
        ).json()
        return readings

    def reset_short_term(self) -> None:
        """Empty the short-term memory."""
        self._session.post(self._url("/short-term/reset"))

    def get_actuators(self) -> dict[str, bool]:
        """Return the current state of every actuator."""
        state: dict[str, bool] = self._session.get(self._url("/actuators")).json()
        return state

    def update_actuators(self, changes: dict[str, bool]) -> dict[str, bool]:
        """Update the given actuators and return the full new state."""
        state: dict[str, bool] = self._session.post(
            self._url("/actuators"), json=changes
        ).json()
        return state
