"""
Abstract base class for all platform adapters.
Each social platform implements this to normalize data into core models.
"""
from abc import ABC, abstractmethod
from typing import Optional
from core.models import FullAnalyticsSnapshot


class BasePlatformAdapter(ABC):
    """
    All social platform integrations inherit from this.
    Implement fetch_snapshot() to pull and normalize platform data.
    """

    PLATFORM_NAME: str = "unknown"

    def __init__(self, base_url: str, auth_token: Optional[str] = None, **kwargs):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self._session_headers: dict = {}
        if auth_token:
            self._session_headers["Authorization"] = f"Bearer {auth_token}"

    @abstractmethod
    def fetch_snapshot(self, days: int = 30, max_content: int = 10) -> FullAnalyticsSnapshot:
        """Fetch all analytics data and return a normalized snapshot."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Verify connectivity and auth are working."""
        ...

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        import requests
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = requests.get(url, headers=self._session_headers, params=params or {})
        response.raise_for_status()
        return response.json()
