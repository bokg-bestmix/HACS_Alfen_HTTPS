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
    PROP_ACTIVE_POWER_L1,
    PROP_ACTIVE_POWER_L2,
    PROP_ACTIVE_POWER_L3,
    PROP_CURRENT_L1,
    PROP_CURRENT_L2,
    PROP_CURRENT_L3,
    PROP_CURRENT_N,
    PROP_ENERGY_L1,
    PROP_ENERGY_L2,
    PROP_ENERGY_L3,
    PROP_ENERGY_TOTAL,
    PROP_FREQUENCY,
    PROP_VOLTAGE_L1L2,
    PROP_VOLTAGE_L1N,
    PROP_VOLTAGE_L2L3,
    PROP_VOLTAGE_L2N,
    PROP_VOLTAGE_L3L1,
    PROP_VOLTAGE_L3N,
)

_LOGGER = logging.getLogger(__name__)

# Property IDs not exported from const (unverified) but still polled for control entities
_PROP_MAX_CURRENT = "2129_0"
_PROP_AVAILABILITY = "2501_0"

_POLLED_PROPS = [
    # Power
    PROP_ACTIVE_POWER,
    PROP_ACTIVE_POWER_L1,
    PROP_ACTIVE_POWER_L2,
    PROP_ACTIVE_POWER_L3,
    # Energy
    PROP_ENERGY_TOTAL,
    PROP_ENERGY_L1,
    PROP_ENERGY_L2,
    PROP_ENERGY_L3,
    # Voltage L-N
    PROP_VOLTAGE_L1N,
    PROP_VOLTAGE_L2N,
    PROP_VOLTAGE_L3N,
    # Voltage L-L
    PROP_VOLTAGE_L1L2,
    PROP_VOLTAGE_L2L3,
    PROP_VOLTAGE_L3L1,
    # Current
    PROP_CURRENT_N,
    PROP_CURRENT_L1,
    PROP_CURRENT_L2,
    PROP_CURRENT_L3,
    # Frequency
    PROP_FREQUENCY,
    # Control (unverified IDs, polled for entity state)
    _PROP_MAX_CURRENT,
    _PROP_AVAILABILITY,
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
