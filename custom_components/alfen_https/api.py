from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import (
    API_INFO,
    API_LOGIN,
    API_LOGOUT,
    API_PROP,
    API_STATUS,
    DEFAULT_PORT,
    PROP_AVAILABILITY,
    PROP_MAX_CURRENT,
)

_LOGGER = logging.getLogger(__name__)


class AlfenApiError(Exception):
    """Raised when an API call fails."""


class AlfenAuthError(AlfenApiError):
    """Raised when authentication fails."""


class AlfenApi:
    """Async client for the Alfen AHP02 local HTTPS REST API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = DEFAULT_PORT,
        verify_ssl: bool = False,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._base_url = f"https://{host}:{port}"
        self._verify_ssl = verify_ssl
        self._session = session
        self._owns_session = session is None
        self._cookie_jar: aiohttp.CookieJar | None = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self._verify_ssl)
            self._cookie_jar = aiohttp.CookieJar()
            self._session = aiohttp.ClientSession(
                connector=connector,
                cookie_jar=self._cookie_jar,
            )
        return self._session

    async def close(self) -> None:
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    async def login(self) -> None:
        session = await self._get_session()
        url = self._base_url + API_LOGIN
        payload = {"username": self._username, "password": self._password}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 401:
                    raise AlfenAuthError("Invalid credentials")
                if resp.status not in (200, 204):
                    raise AlfenApiError(f"Login failed with status {resp.status}")
        except aiohttp.ClientError as exc:
            raise AlfenApiError(f"Connection error during login: {exc}") from exc

    async def logout(self) -> None:
        try:
            session = await self._get_session()
            url = self._base_url + API_LOGOUT
            async with session.post(url) as resp:
                if resp.status not in (200, 204):
                    _LOGGER.debug("Logout returned status %s", resp.status)
        except aiohttp.ClientError as exc:
            _LOGGER.debug("Error during logout: %s", exc)

    # ------------------------------------------------------------------
    # Data retrieval
    # ------------------------------------------------------------------

    async def get_info(self) -> dict[str, Any]:
        return await self._get(API_INFO)

    async def get_status(self) -> dict[str, Any]:
        return await self._get(API_STATUS)

    async def get_properties(self, ids: list[str] | None = None) -> dict[str, Any]:
        """Return properties. Optionally filter by property ID list."""
        data = await self._get(API_PROP)
        props: dict[str, Any] = {}
        for entry in data.get("properties", []):
            prop_id = entry.get("id")
            if prop_id and (ids is None or prop_id in ids):
                props[prop_id] = entry.get("value")
        return props

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    async def set_max_current(self, ampere: float) -> None:
        await self._post_prop(PROP_MAX_CURRENT, ampere)

    async def set_availability(self, available: bool) -> None:
        await self._post_prop(PROP_AVAILABILITY, 1 if available else 2)

    # ------------------------------------------------------------------
    # Connectivity test (used by config flow)
    # ------------------------------------------------------------------

    async def test_connection(self) -> str:
        """Login, fetch serial, logout. Returns serial number on success."""
        await self.login()
        try:
            info = await self.get_info()
            serial: str = info.get("serial", "")
            if not serial:
                raise AlfenApiError("Charger returned empty serial number")
            return serial
        finally:
            await self.logout()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str) -> dict[str, Any]:
        session = await self._get_session()
        url = self._base_url + path
        try:
            async with session.get(url) as resp:
                if resp.status == 401:
                    raise AlfenAuthError("Session expired — re-login required")
                if resp.status != 200:
                    raise AlfenApiError(f"GET {path} returned {resp.status}")
                return await resp.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise AlfenApiError(f"Request error for {path}: {exc}") from exc

    async def _post_prop(self, prop_id: str, value: Any) -> None:
        session = await self._get_session()
        url = self._base_url + API_PROP
        payload = {"properties": [{"id": prop_id, "value": value}]}
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 401:
                    raise AlfenAuthError("Session expired — re-login required")
                if resp.status not in (200, 204):
                    raise AlfenApiError(
                        f"POST prop {prop_id}={value} returned {resp.status}"
                    )
        except aiohttp.ClientError as exc:
            raise AlfenApiError(f"Request error writing prop {prop_id}: {exc}") from exc
