"""Constants for the Luke Roberts integration."""

DOMAIN = "luke_roberts"

# Configuration
CONF_API_TOKEN = "api_token"
CONF_LAMP_ID = "lamp_id"
CONF_DEVICE_NAME = "device_name"

# Defaults
DEFAULT_SCAN_INTERVAL = 30

# API Configuration
API_BASE_URL = "https://cloud.luke-roberts.com/api/v1"
API_TIMEOUT = 10

# API Endpoints
ENDPOINT_LAMPS = "/lamps"
ENDPOINT_LAMP_STATE = "/lamps/{lamp_id}/state"
ENDPOINT_LAMP_COMMAND = "/lamps/{lamp_id}/command"

# Power States
STATE_ON = "ON"
STATE_OFF = "OFF"

# Color Temperature Range (in Kelvin)
MIN_KELVIN = 2700
MAX_KELVIN = 4000

# Color Temperature Range (in mireds)
MIN_MIREDS = 250  # 4000K
MAX_MIREDS = 370  # 2700K

# Brightness Range
MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 100
