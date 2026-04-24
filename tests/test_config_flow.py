"""Tests for the AlfenConfigFlow UI setup flow."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.alfen_https.api import AlfenApiError, AlfenAuthError
from custom_components.alfen_https.const import CONF_VERIFY_SSL, DOMAIN

from .conftest import MOCK_HOST, MOCK_PASSWORD, MOCK_SERIAL, MOCK_USERNAME

_USER_INPUT = {
    CONF_HOST: MOCK_HOST,
    CONF_USERNAME: MOCK_USERNAME,
    CONF_PASSWORD: MOCK_PASSWORD,
    CONF_VERIFY_SSL: False,
}


async def test_full_user_flow_success(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as mock_cls:
        api = mock_cls.return_value
        api.test_connection = AsyncMock(return_value=MOCK_SERIAL)
        api.close = AsyncMock()

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_USER_INPUT,
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Alfen {MOCK_HOST}"
    assert result["data"][CONF_HOST] == MOCK_HOST


async def test_flow_invalid_auth(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as mock_cls:
        api = mock_cls.return_value
        api.test_connection = AsyncMock(side_effect=AlfenAuthError("bad creds"))
        api.close = AsyncMock()

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_USER_INPUT,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_flow_cannot_connect(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as mock_cls:
        api = mock_cls.return_value
        api.test_connection = AsyncMock(side_effect=AlfenApiError("timeout"))
        api.close = AsyncMock()

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_USER_INPUT,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_flow_unknown_exception(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as mock_cls:
        api = mock_cls.return_value
        api.test_connection = AsyncMock(side_effect=Exception("unexpected"))
        api.close = AsyncMock()

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=_USER_INPUT,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


async def test_flow_already_configured(hass: HomeAssistant) -> None:
    """Second setup with the same serial is aborted."""
    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as mock_cls:
        api = mock_cls.return_value
        api.test_connection = AsyncMock(return_value=MOCK_SERIAL)
        api.close = AsyncMock()

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=_USER_INPUT
        )

    # Second attempt with same serial
    with patch(
        "custom_components.alfen_https.config_flow.AlfenApi"
    ) as mock_cls:
        api = mock_cls.return_value
        api.test_connection = AsyncMock(return_value=MOCK_SERIAL)
        api.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result2["flow_id"], user_input=_USER_INPUT
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
