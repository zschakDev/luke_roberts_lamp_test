"""The Luke Roberts integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import LukeRobertsApi
from .const import CONF_API_TOKEN, CONF_DEVICE_NAME, CONF_LAMP_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Luke Roberts from a config entry."""
    api_token = entry.data[CONF_API_TOKEN]
    lamp_id = entry.data[CONF_LAMP_ID]

    api = LukeRobertsApi(api_token=api_token, lamp_id=lamp_id)

    # Test connection
    if not await api.test_connection():
        await api.close()
        raise ConfigEntryNotReady(f"Unable to connect to Luke Roberts lamp {lamp_id}")

    # Store API instance
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    # Forward the setup to the light platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Close API connection
        api: LukeRobertsApi = hass.data[DOMAIN][entry.entry_id]
        await api.close()

        # Remove entry from data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
