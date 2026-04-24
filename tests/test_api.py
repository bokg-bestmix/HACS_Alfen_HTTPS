"""Unit tests for AlfenApi — mocks aiohttp at the session level."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.alfen_https.api import AlfenApi, AlfenApiError, AlfenAuthError
from custom_components.alfen_https.const import PROP_MAX_CURRENT

from .conftest import MOCK_HOST, MOCK_PASSWORD, MOCK_SERIAL, MOCK_USERNAME


def _make_response(status: int, json_data: dict | None = None) -> MagicMock:
    """Build a minimal aiohttp response mock usable as an async context manager."""
    resp = MagicMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {})
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _make_api(**kwargs) -> AlfenApi:
    return AlfenApi(
        host=MOCK_HOST,
        username=MOCK_USERNAME,
        password=MOCK_PASSWORD,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


async def test_login_success() -> None:
    api = _make_api()
    resp = _make_response(200)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.post.return_value = resp
        mock_get_session.return_value = session

        await api.login()

        session.post.assert_called_once()
        call_kwargs = session.post.call_args
        assert "/api/login" in call_kwargs[0][0]


async def test_login_401_raises_auth_error() -> None:
    api = _make_api()
    resp = _make_response(401)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.post.return_value = resp
        mock_get_session.return_value = session

        with pytest.raises(AlfenAuthError):
            await api.login()


async def test_login_500_raises_api_error() -> None:
    api = _make_api()
    resp = _make_response(500)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.post.return_value = resp
        mock_get_session.return_value = session

        with pytest.raises(AlfenApiError):
            await api.login()


async def test_login_connection_error_raises_api_error() -> None:
    api = _make_api()
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.post.side_effect = aiohttp.ClientConnectionError("refused")
        mock_get_session.return_value = session

        with pytest.raises(AlfenApiError, match="Connection error"):
            await api.login()


# ---------------------------------------------------------------------------
# get_properties
# ---------------------------------------------------------------------------


async def test_get_properties_returns_parsed_dict() -> None:
    api = _make_api()
    raw = {
        "properties": [
            {"id": "2221_0", "value": 3680.0},
            {"id": "2129_0", "value": 16.0},
            {"id": "2060_0", "value": 3},
        ]
    }
    resp = _make_response(200, raw)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.get.return_value = resp
        mock_get_session.return_value = session

        props = await api.get_properties()

    assert props["2221_0"] == 3680.0
    assert props["2129_0"] == 16.0
    assert props["2060_0"] == 3


async def test_get_properties_filters_by_id() -> None:
    api = _make_api()
    raw = {
        "properties": [
            {"id": "2221_0", "value": 3680.0},
            {"id": "2129_0", "value": 16.0},
        ]
    }
    resp = _make_response(200, raw)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.get.return_value = resp
        mock_get_session.return_value = session

        props = await api.get_properties(["2221_0"])

    assert "2221_0" in props
    assert "2129_0" not in props


async def test_get_session_expired_raises_auth_error() -> None:
    api = _make_api()
    resp = _make_response(401)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.get.return_value = resp
        mock_get_session.return_value = session

        with pytest.raises(AlfenAuthError, match="Session expired"):
            await api.get_properties()


# ---------------------------------------------------------------------------
# set_max_current / _post_prop
# ---------------------------------------------------------------------------


async def test_set_max_current_posts_correct_payload() -> None:
    api = _make_api()
    resp = _make_response(204)
    with patch.object(api, "_get_session") as mock_get_session:
        session = MagicMock()
        session.post.return_value = resp
        mock_get_session.return_value = session

        await api.set_max_current(20.0)

        _, kwargs = session.post.call_args
        props = kwargs["json"]["properties"]
        assert props[0]["id"] == PROP_MAX_CURRENT
        assert props[0]["value"] == 20.0


# ---------------------------------------------------------------------------
# test_connection
# ---------------------------------------------------------------------------


async def test_test_connection_returns_serial() -> None:
    api = _make_api()
    api.login = AsyncMock()
    api.logout = AsyncMock()
    api.get_info = AsyncMock(return_value={"serial": MOCK_SERIAL})

    serial = await api.test_connection()

    assert serial == MOCK_SERIAL
    api.login.assert_awaited_once()
    api.logout.assert_awaited_once()


async def test_test_connection_empty_serial_raises() -> None:
    api = _make_api()
    api.login = AsyncMock()
    api.logout = AsyncMock()
    api.get_info = AsyncMock(return_value={"serial": ""})

    with pytest.raises(AlfenApiError, match="empty serial"):
        await api.test_connection()


async def test_test_connection_always_logs_out_on_error() -> None:
    api = _make_api()
    api.login = AsyncMock()
    api.logout = AsyncMock()
    api.get_info = AsyncMock(side_effect=AlfenApiError("boom"))

    with pytest.raises(AlfenApiError):
        await api.test_connection()

    api.logout.assert_awaited_once()
