from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AlfenApi, AlfenAuthError, AlfenApiError
from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    PROP_ACTIVE_POWER,
    PROP_AVAILABILITY,
    PROP_CONNECTOR_STATE,
    PROP_MAX_CURRENT,
    PROP_SESSION_ENERGY,
)

_LOGGER = logging.getLogger(__name__)

_POLLED_PROPS = [
    PROP_ACTIVE_POWER,
    PROP_SESSION_ENERGY,
    PROP_MAX_CURRENT,
    PROP_AVAILABILITY,
    PROP_CONNECTOR_STATE,
]


class AlfenCoordinatorData:
    """Typed container for a single poll result."""

    def __init__(
        self,
        properties: dict[str, Any],
        status: dict[str, Any],
    ) -> None:
        self.properties = properties
        self.status = status

    def prop(self, prop_id: str) -> Any:
        return self.properties.get(prop_id)


class AlfenDataUpdateCoordinator(DataUpdateCoordinator[AlfenCoordinatorData]):
    """Coordinator that keeps all entities in sync with a single poll cycle."""

    def __init__(self, hass: HomeAssistant, api: AlfenApi, serial: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{serial}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self.serial = serial

    async def _async_update_data(self) -> AlfenCoordinatorData:
        try:
            await self.api.login()
            try:
                props, status = await self._fetch_all()
            finally:
                await self.api.logout()
        except AlfenAuthError as exc:
            raise ConfigEntryAuthFailed(str(exc)) from exc
        except AlfenApiError as exc:
            raise UpdateFailed(str(exc)) from exc

        return AlfenCoordinatorData(properties=props, status=status)

    async def _fetch_all(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        props = await self.api.get_properties(_POLLED_PROPS)
        status = await self.api.get_status()
        return props, status
