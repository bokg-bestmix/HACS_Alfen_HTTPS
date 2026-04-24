from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AlfenApiError
from .const import DOMAIN, PROP_AVAILABILITY
from .coordinator import AlfenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Availability property values: 1 = operative (charging allowed), 2 = inoperative
_AVAILABLE_VALUE = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AlfenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AlfenAvailabilitySwitch(coordinator)])


class AlfenAvailabilitySwitch(CoordinatorEntity[AlfenDataUpdateCoordinator], SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Charging Enabled"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: AlfenDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.serial}_{PROP_AVAILABILITY}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.serial)},
            "name": "Alfen Charger",
            "manufacturer": "Alfen",
            "model": "AHP02",
            "serial_number": coordinator.serial,
        }

    @property
    def is_on(self) -> bool | None:
        raw = self.coordinator.data.prop(PROP_AVAILABILITY)
        if raw is None:
            return None
        return int(raw) == _AVAILABLE_VALUE

    async def async_turn_on(self, **kwargs: Any) -> None:
        try:
            await self.coordinator.api.login()
            await self.coordinator.api.set_availability(True)
            await self.coordinator.api.logout()
        except AlfenApiError as exc:
            _LOGGER.error("Failed to enable charging: %s", exc)
            return
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        try:
            await self.coordinator.api.login()
            await self.coordinator.api.set_availability(False)
            await self.coordinator.api.logout()
        except AlfenApiError as exc:
            _LOGGER.error("Failed to disable charging: %s", exc)
            return
        await self.coordinator.async_request_refresh()
