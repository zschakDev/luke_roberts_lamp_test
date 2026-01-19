"""Constants for the Luke Roberts integration."""

DOMAIN = "luke_roberts"

# Configuration
CONF_HOST = "host"
CONF_PORT = "port"
CONF_DEVICE_NAME = "device_name"

# Defaults
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30

# API Commands
CMD_POWER = "POWER"
CMD_DIMMER = "DIMMER"
CMD_CT = "CT"
CMD_KELVIN = "KELVIN"
CMD_UPLIGHT = "UPLIGHT"
CMD_DOWNLIGHT = "DOWNLIGHT"
CMD_STATE = "STATE"

# Power States
STATE_ON = "ON"
STATE_OFF = "OFF"

# Color Temperature Range (in mireds)
MIN_MIREDS = 250  # 4000K
MAX_MIREDS = 416  # 2404K (~2700K)

# Color Temperature Range (in Kelvin)
MIN_KELVIN = 2700
MAX_KELVIN = 4000

# Brightness Range
MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 100

# API Endpoints
API_PATH = "/cm"
