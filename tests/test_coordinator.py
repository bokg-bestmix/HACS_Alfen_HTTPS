"""Tests for AlfenDataUpdateCoordinator."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.alfen_https.api import AlfenApiError, AlfenAuthError
from custom_components.alfen_https.const import PROP_ACTIVE_POWER, PROP_CONNECTOR_STATE
from custom_components.alfen_https.coordinator import AlfenDataUpdateCoordinator

from .conftest import MOCK_PROPERTIES, MOCK_SERIAL, MOCK_STATUS


def _make_api(
    properties: dict | None = None,
    status: dict | None = None,
) -> MagicMock:
    api = MagicMock()
    api.login = AsyncMock()
    api.logout = AsyncMock()
    api.get_properties = AsyncMock(return_value=properties or MOCK_PROPERTIES)
    api.get_status = AsyncMock(return_value=status or MOCK_STATUS)
    return api


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


async def test_coordinator_first_refresh(hass: HomeAssistant) -> None:
    api = _make_api()
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    await coordinator.async_config_entry_first_refresh()

    assert coordinator.data is not None
    assert coordinator.data.prop(PROP_ACTIVE_POWER) == MOCK_PROPERTIES[PROP_ACTIVE_POWER]


async def test_coordinator_login_logout_called_each_cycle(hass: HomeAssistant) -> None:
    api = _make_api()
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    await coordinator.async_config_entry_first_refresh()

    api.login.assert_awaited_once()
    api.logout.assert_awaited_once()


async def test_coordinator_data_contains_all_props(hass: HomeAssistant) -> None:
    api = _make_api()
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    await coordinator.async_config_entry_first_refresh()

    for prop_id, value in MOCK_PROPERTIES.items():
        assert coordinator.data.prop(prop_id) == value


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


async def test_coordinator_auth_error_raises_config_entry_auth_failed(
    hass: HomeAssistant,
) -> None:
    api = _make_api()
    api.login = AsyncMock(side_effect=AlfenAuthError("bad token"))
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator.async_config_entry_first_refresh()


async def test_coordinator_api_error_raises_update_failed(
    hass: HomeAssistant,
) -> None:
    api = _make_api()
    api.get_properties = AsyncMock(side_effect=AlfenApiError("timeout"))
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    with pytest.raises(UpdateFailed):
        await coordinator.async_config_entry_first_refresh()


async def test_coordinator_logout_called_even_when_fetch_fails(
    hass: HomeAssistant,
) -> None:
    api = _make_api()
    api.get_properties = AsyncMock(side_effect=AlfenApiError("timeout"))
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    with pytest.raises(UpdateFailed):
        await coordinator.async_config_entry_first_refresh()

    api.logout.assert_awaited_once()


# ---------------------------------------------------------------------------
# CoordinatorData helper
# ---------------------------------------------------------------------------


async def test_coordinator_data_prop_returns_none_for_missing_key(
    hass: HomeAssistant,
) -> None:
    api = _make_api(properties={})
    coordinator = AlfenDataUpdateCoordinator(hass, api, MOCK_SERIAL)

    await coordinator.async_config_entry_first_refresh()

    assert coordinator.data.prop("nonexistent") is None
