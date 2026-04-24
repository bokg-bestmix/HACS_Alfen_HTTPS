from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AlfenApi, AlfenApiError, AlfenAuthError
from .const import CONF_VERIFY_SSL, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default="admin"): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_VERIFY_SSL, default=False): bool,
    }
)


class AlfenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup UI flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            verify_ssl = user_input.get(CONF_VERIFY_SSL, False)

            api = AlfenApi(
                host=host,
                username=username,
                password=password,
                port=DEFAULT_PORT,
                verify_ssl=verify_ssl,
            )

            try:
                serial = await api.test_connection()
            except AlfenAuthError:
                errors["base"] = "invalid_auth"
            except AlfenApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Alfen {host}",
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_VERIFY_SSL: verify_ssl,
                    },
                )
            finally:
                await api.close()

        return self.async_show_form(
            step_id="user",
            data_schema=_STEP_SCHEMA,
            errors=errors,
        )
