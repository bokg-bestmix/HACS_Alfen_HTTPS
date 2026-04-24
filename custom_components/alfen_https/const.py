DOMAIN = "alfen_https"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_VERIFY_SSL = "verify_ssl"

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 443

# API paths
API_LOGIN = "/api/login"
API_LOGOUT = "/api/logout"
API_INFO = "/api/info"
API_STATUS = "/api/status"
API_PROP = "/api/prop"

# AHP02 property IDs
# NOTE: verify all IDs against your device's /api/prop response before shipping
PROP_ACTIVE_POWER = "2221_0"       # Total active power (W), sum of all phases
PROP_ACTIVE_POWER_L1 = "2221_4"   # Active power phase L1 (W)
PROP_ACTIVE_POWER_L2 = "2221_5"   # Active power phase L2 (W)
PROP_ACTIVE_POWER_L3 = "2221_6"   # Active power phase L3 (W)
PROP_SESSION_ENERGY = "2221_3"
PROP_ENERGY_TOTAL = "2062_0"      # Cumulative energy all phases (Wh) — verify against device
PROP_ENERGY_L1 = "2062_1"         # Cumulative energy L1 (Wh) — verify against device
PROP_ENERGY_L2 = "2062_2"         # Cumulative energy L2 (Wh) — verify against device
PROP_ENERGY_L3 = "2062_3"         # Cumulative energy L3 (Wh) — verify against device
PROP_MAX_CURRENT = "2129_0"
PROP_AVAILABILITY = "2501_0"
PROP_CONNECTOR_STATE = "2060_0"

# Connector state enum
CONNECTOR_STATE_AVAILABLE = 0
CONNECTOR_STATE_PREPARING = 1
CONNECTOR_STATE_CHARGING = 3
CONNECTOR_STATE_FINISHING = 5
CONNECTOR_STATE_FAULTED = 9

CONNECTOR_STATE_MAP = {
    CONNECTOR_STATE_AVAILABLE: "available",
    CONNECTOR_STATE_PREPARING: "preparing",
    CONNECTOR_STATE_CHARGING: "charging",
    CONNECTOR_STATE_FINISHING: "finishing",
    CONNECTOR_STATE_FAULTED: "faulted",
}
