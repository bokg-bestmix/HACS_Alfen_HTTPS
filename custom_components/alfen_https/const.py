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

# Voltage L-N (line to neutral) — verify IDs against device
PROP_VOLTAGE_L1N = "2221_3"
PROP_VOLTAGE_L2N = "2221_4"
PROP_VOLTAGE_L3N = "2221_5"

# Voltage L-L (line to line) — verify IDs against device
PROP_VOLTAGE_L1L2 = "2221_6"
PROP_VOLTAGE_L2L3 = "2221_7"
PROP_VOLTAGE_L3L1 = "2221_8"

# Current — verify IDs against device
PROP_CURRENT_N  = "2212_9"
PROP_CURRENT_L1 = "2212_A"
PROP_CURRENT_L2 = "2212_B"
PROP_CURRENT_L3 = "2212_C"

# Frequency — verify ID against device
PROP_FREQUENCY = "2221_12"

# Active power — verify IDs against device
PROP_ACTIVE_POWER_L1 = "2221_13"   # Active power phase L1 (W)
PROP_ACTIVE_POWER_L2 = "2221_14"   # Active power phase L2 (W)
PROP_ACTIVE_POWER_L3 = "2221_15"   # Active power phase L3 (W)
PROP_ACTIVE_POWER = "2221_16"      # Total active power (W), sum of all phases

PROP_ENERGY_L1 = "2221_1F"         # Cumulative energy L1 (Wh) — verify against device
PROP_ENERGY_L2 = "2221_20"         # Cumulative energy L2 (Wh) — verify against device
PROP_ENERGY_L3 = "2221_21"         # Cumulative energy L3 (Wh) — verify against device
PROP_ENERGY_TOTAL = "2221_22"      # Cumulative energy all phases (Wh) — verify against device

# # Disable for now until we can verify IDs against device
PROP_SESSION_ENERGY = "2221_3"
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
