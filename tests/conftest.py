"""Shared fixtures for alfen_https tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from custom_components.alfen_https.const import (
    CONF_VERIFY_SSL,
    CONNECTOR_STATE_CHARGING,
    DOMAIN,
    PROP_ACTIVE_POWER,
    PROP_AVAILABILITY,
    PROP_CONNECTOR_STATE,
    PROP_MAX_CURRENT,
    PROP_SESSION_ENERGY,
)
from custom_components.alfen_https.coordinator import AlfenCoordinatorData

MOCK_HOST = "192.168.1.100"
MOCK_USERNAME = "admin"
MOCK_PASSWORD = "admin"
MOCK_SERIAL = "ACE0000001"

MOCK_ENTRY_DATA = {
    CONF_HOST: MOCK_HOST,
    CONF_USERNAME: MOCK_USERNAME,
    CONF_PASSWORD: MOCK_PASSWORD,
    CONF_VERIFY_SSL: False,
}

MOCK_PROPERTIES = {
    PROP_ACTIVE_POWER: 3680.0,
    PROP_SESSION_ENERGY: 12500.0,
    PROP_MAX_CURRENT: 16.0,
    PROP_AVAILABILITY: 1,
    PROP_CONNECTOR_STATE: CONNECTOR_STATE_CHARGING,
}

MOCK_STATUS = {
    "status": "connected",
}


def build_coordinator_data(
    properties: dict | None = None,
    status: dict | None = None,
) -> AlfenCoordinatorData:
    return AlfenCoordinatorData(
        properties=properties or MOCK_PROPERTIES,
        status=status or MOCK_STATUS,
    )


@pytest.fixture
def mock_api() -> Generator[MagicMock, None, None]:
    """Patch AlfenApi everywhere it is imported and return a pre-configured mock."""
    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as flow_mock_cls, patch(
        "custom_components.alfen_https.__init__.AlfenApi"
    ) as init_mock_cls:
        api = MagicMock()
        api.login = AsyncMock()
        api.logout = AsyncMock()
        api.close = AsyncMock()
        api.test_connection = AsyncMock(return_value=MOCK_SERIAL)
        api.get_info = AsyncMock(return_value={"serial": MOCK_SERIAL, "model": "Eve Double Pro-line"})
        api.get_status = AsyncMock(return_value=MOCK_STATUS)
        api.get_properties = AsyncMock(return_value=MOCK_PROPERTIES)
        api.set_max_current = AsyncMock()
        api.set_availability = AsyncMock()

        flow_mock_cls.return_value = api
        init_mock_cls.return_value = api

        yield api


@pytest.fixture
def config_entry(hass: HomeAssistant) -> ConfigEntry:
    """Return a mock config entry already added to hass."""
    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title=f"Alfen {MOCK_HOST}",
        data=MOCK_ENTRY_DATA,
        source="user",
        unique_id=MOCK_SERIAL,
        options={},
    )
    entry._hass = hass
    return entry


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    mock_api: MagicMock,
) -> ConfigEntry:
    """Set up the integration and return the config entry."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
