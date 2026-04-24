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
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
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
        key="active_power_l1",
        prop_id=PROP_ACTIVE_POWER_L1,
        name="Active Power L1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="active_power_l2",
        prop_id=PROP_ACTIVE_POWER_L2,
        name="Active Power L2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="active_power_l3",
        prop_id=PROP_ACTIVE_POWER_L3,
        name="Active Power L3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="energy_total",
        prop_id=PROP_ENERGY_TOTAL,
        name="Total Energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AlfenSensorEntityDescription(
        key="energy_l1",
        prop_id=PROP_ENERGY_L1,
        name="Total Energy L1",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AlfenSensorEntityDescription(
        key="energy_l2",
        prop_id=PROP_ENERGY_L2,
        name="Total Energy L2",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AlfenSensorEntityDescription(
        key="energy_l3",
        prop_id=PROP_ENERGY_L3,
        name="Total Energy L3",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    # Voltage L-N
    AlfenSensorEntityDescription(
        key="voltage_l1n",
        prop_id=PROP_VOLTAGE_L1N,
        name="Voltage L1-N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="voltage_l2n",
        prop_id=PROP_VOLTAGE_L2N,
        name="Voltage L2-N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="voltage_l3n",
        prop_id=PROP_VOLTAGE_L3N,
        name="Voltage L3-N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Voltage L-L
    AlfenSensorEntityDescription(
        key="voltage_l1l2",
        prop_id=PROP_VOLTAGE_L1L2,
        name="Voltage L1-L2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="voltage_l2l3",
        prop_id=PROP_VOLTAGE_L2L3,
        name="Voltage L2-L3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="voltage_l3l1",
        prop_id=PROP_VOLTAGE_L3L1,
        name="Voltage L3-L1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Current
    AlfenSensorEntityDescription(
        key="current_n",
        prop_id=PROP_CURRENT_N,
        name="Current N",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="current_l1",
        prop_id=PROP_CURRENT_L1,
        name="Current L1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="current_l2",
        prop_id=PROP_CURRENT_L2,
        name="Current L2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AlfenSensorEntityDescription(
        key="current_l3",
        prop_id=PROP_CURRENT_L3,
        name="Current L3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # Frequency
    AlfenSensorEntityDescription(
        key="frequency",
        prop_id=PROP_FREQUENCY,
        name="Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
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
