# HACS Alfen HTTPS — Claude Code Guide

## Project Goal

Build a HACS-compatible Home Assistant custom integration for Alfen EV charge stations running on the **Alfen Hardware Platform 02 (AHP02)**. Communication uses the local HTTPS REST API exposed by AHP02 devices (no Modbus, no cloud dependency).

---

## Target Device

| Property | Value |
|---|---|
| Brand | Alfen |
| Hardware platform | AHP02 (Alfen Hardware Platform 02) |
| Protocol | HTTPS REST (local network) |
| Auth | Session cookie via `POST /api/login` |
| Default host | `<charger-ip>` (user-configured) |
| TLS | Self-signed certificate — SSL verification must be disabled or the cert pinned |

Known AHP02 API base path: `/api/` (e.g., `https://<ip>/api/info`, `https://<ip>/api/status`, `https://<ip>/api/prop`).

---

## Directory Layout (target state)

```
HACS_Alfen_HTTPS/
├── custom_components/
│   └── alfen_https/
│       ├── __init__.py          # Integration setup / async_setup_entry
│       ├── manifest.json        # HA manifest (domain, version, deps)
│       ├── config_flow.py       # UI config flow (host, username, password)
│       ├── const.py             # Domain constant, API paths, default values
│       ├── coordinator.py       # DataUpdateCoordinator — polls the charger
│       ├── api.py               # Async HTTP client wrapper (aiohttp)
│       ├── sensor.py            # Sensor entities (power, energy, state, …)
│       ├── switch.py            # Switch entities (charging enable/disable)
│       ├── number.py            # Number entities (max current)
│       ├── strings.json         # Translation strings (en)
│       └── translations/
│           └── en.json
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── hacs.json                    # HACS metadata
├── CLAUDE.md
├── README.md
└── .gitignore
```

---

## Technology Stack

- **Language**: Python 3.12+
- **HA core dependency**: `homeassistant >= 2024.1`
- **HTTP client**: `aiohttp` (already bundled with HA; no extra deps needed)
- **Testing**: `pytest`, `pytest-asyncio`, `pytest-homeassistant-custom-component`
- **Linting/format**: `ruff` (format + lint), `mypy` (type checking)

---

## Key Architecture Decisions

1. **Single `DataUpdateCoordinator`** polls the charger every 30 seconds. All entities read from `coordinator.data` — never make their own API calls.
2. **`api.py`** owns all HTTP logic. It handles login, token refresh, and exposes typed methods (`get_status()`, `get_properties()`, `set_max_current()`). It must never be called directly from entities.
3. **Config flow** collects host, username, password. It validates connectivity during setup (calls `api.test_connection()`).
4. **SSL**: use `aiohttp.TCPConnector(ssl=False)` for now; add a UI toggle "Verify SSL" in a later iteration.
5. **Unique ID**: use the charger's serial number from `/api/info` as the config entry unique ID to prevent duplicates.

---

## Alfen AHP02 REST API Reference

All endpoints require an active session obtained via login. The session is maintained via a cookie.

```
POST  /api/login              body: {"username": "…", "password": "…"}
POST  /api/logout
GET   /api/info               charger identity (serial, model, firmware)
GET   /api/status             live status (connector state, current session)
GET   /api/prop               all properties (flat key/value list)
POST  /api/prop               write property values
```

Important property IDs (AHP02):
| Property ID | Description |
|---|---|
| `2221_0` | Active power total — sum of all phases (W) |
| `2221_4` | Active power L1 (W) — **verify against device** |
| `2221_5` | Active power L2 (W) — **verify against device** |
| `2221_6` | Active power L3 (W) — **verify against device** |
| `2221_3` | Session energy (Wh) |
| `2062_0` | Cumulative energy total — all phases (Wh) — **verify against device** |
| `2062_1` | Cumulative energy L1 (Wh) — **verify against device** |
| `2062_2` | Cumulative energy L2 (Wh) — **verify against device** |
| `2062_3` | Cumulative energy L3 (Wh) — **verify against device** |
| `2129_0` | Max charge current setpoint (A) |
| `2501_0` | Availability (enable/disable charging) |
| `2060_0` | Connector state (enum) |

Connector state enum: `0` = Available, `1` = Preparing, `3` = Charging, `5` = Finishing, `9` = Faulted.

---

## HACS Compliance Requirements

`hacs.json` must exist at repo root:
```json
{
  "name": "Alfen HTTPS",
  "render_readme": true
}
```

`custom_components/alfen_https/manifest.json` required fields:
```json
{
  "domain": "alfen_https",
  "name": "Alfen HTTPS",
  "version": "0.1.0",
  "codeowners": ["@bokg-bestmix"],
  "config_flow": true,
  "documentation": "https://github.com/bokg-bestmix/HACS_Alfen_HTTPS",
  "iot_class": "local_polling",
  "requirements": []
}
```

---

## Development Setup

```bash
# Create and activate venv
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dev dependencies
pip install homeassistant ruff mypy pytest pytest-asyncio \
            pytest-homeassistant-custom-component

# Lint + format
ruff check custom_components/
ruff format custom_components/

# Type check
mypy custom_components/alfen_https/

# Run tests
pytest tests/ -v
```

---

## Coding Conventions

- Async everywhere — no blocking I/O on the event loop.
- Type-annotate all public functions and methods.
- Log with `logging.getLogger(__name__)` — use `_LOGGER` as the module-level variable name.
- Raise `ConfigEntryNotReady` from `async_setup_entry` if the charger is unreachable on startup.
- Raise `UpdateFailed` inside the coordinator's `_async_update_data` on polling errors.
- Entity `unique_id` pattern: `{serial}_{property_id}` (e.g., `ABC123_2221_0`).

---

## Out of Scope (for now)

- OCPP / cloud relay
- Modbus TCP
- Multi-socket chargers (AHP02 single-socket only)
- Energy dashboard integration (add in v0.2 once core entities are stable)