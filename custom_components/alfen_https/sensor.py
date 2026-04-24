from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONNECTOR_STATE_MAP,
    DOMAIN,
    PROP_ACTIVE_POWER,
    PROP_CONNECTOR_STATE,
    PROP_SESSION_ENERGY,
)
from .coordinator import AlfenCoordinatorData, AlfenDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class AlfenSensorEntityDescription(SensorEntityDescription):
    prop_id: str
    value_fn: Any = None  # optional transform applied to the raw property value


SENSOR_DESCRIPTIONS: tuple[AlfenSensorEntityDescription, ...] = (
    AlfenSensorEntityDescription(
        key="active_power",
        prop_id=PROP_ACTIVE_POWER,
        name="Active Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="session_energy",
        prop_id=PROP_SESSION_ENERGY,
        name="Session Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AlfenSensorEntityDescription(
        key="connector_state",
        prop_id=PROP_CONNECTOR_STATE,
        name="Connector State",
        device_class=SensorDeviceClass.ENUM,
        options=list(CONNECTOR_STATE_MAP.values()),
        value_fn=lambda v: CONNECTOR_STATE_MAP.get(int(v), "unknown") if v is not None else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AlfenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AlfenSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class AlfenSensor(CoordinatorEntity[AlfenDataUpdateCoordinator], SensorEntity):
    entity_description: AlfenSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlfenDataUpdateCoordinator,
        description: AlfenSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial}_{description.prop_id}"
        self._attr_device_info = _device_info(coordinator)

    @property
    def native_value(self) -> Any:
        raw = self.coordinator.data.prop(self.entity_description.prop_id)
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(raw)
        return raw


def _device_info(coordinator: AlfenDataUpdateCoordinator) -> dict:
    return {
        "identifiers": {(DOMAIN, coordinator.serial)},
        "name": "Alfen Charger",
        "manufacturer": "Alfen",
        "model": "AHP02",
        "serial_number": coordinator.serial,
    }
