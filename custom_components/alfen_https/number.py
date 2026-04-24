from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AlfenApiError
from .const import DOMAIN
from .coordinator import AlfenDataUpdateCoordinator

__PROP_MAX_CURRENT = "2129_0"

_LOGGER = logging.getLogger(__name__)

# AHP02 supports 6–32 A on a single-phase or three-phase circuit
_MIN_CURRENT = 6.0
_MAX_CURRENT = 32.0
_STEP_CURRENT = 1.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AlfenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AlfenMaxCurrentNumber(coordinator)])


class AlfenMaxCurrentNumber(CoordinatorEntity[AlfenDataUpdateCoordinator], NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Max Charge Current"
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = _MIN_CURRENT
    _attr_native_max_value = _MAX_CURRENT
    _attr_native_step = _STEP_CURRENT
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: AlfenDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.serial}_{_PROP_MAX_CURRENT}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.serial)},
            "name": "Alfen Charger",
            "manufacturer": "Alfen",
            "model": "AHP02",
            "serial_number": coordinator.serial,
        }

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.data.prop(_PROP_MAX_CURRENT)
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        try:
            await self.coordinator.api.login()
            await self.coordinator.api.set_max_current(value)
            await self.coordinator.api.logout()
        except AlfenApiError as exc:
            _LOGGER.error("Failed to set max current to %sA: %s", value, exc)
            return
        await self.coordinator.async_request_refresh()
