from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import AlfenApi, AlfenApiError
from .const import CONF_VERIFY_SSL, DEFAULT_PORT, DOMAIN
from .coordinator import AlfenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = AlfenApi(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        port=DEFAULT_PORT,
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, False),
    )

    serial = entry.unique_id or entry.data[CONF_HOST]

    coordinator = AlfenDataUpdateCoordinator(hass, api, serial)

    try:
        await coordinator.async_config_entry_first_refresh()
    except AlfenApiError as exc:
        await api.close()
        raise ConfigEntryNotReady(f"Cannot connect to charger: {exc}") from exc

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator: AlfenDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.close()
    return unloaded
