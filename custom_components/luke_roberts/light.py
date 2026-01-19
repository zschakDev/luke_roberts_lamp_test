"""Light platform for Luke Roberts integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.color as color_util

from .api import LukeRobertsApi
from .const import (
    CONF_DEVICE_NAME,
    DOMAIN,
    MAX_BRIGHTNESS,
    MAX_KELVIN,
    MIN_BRIGHTNESS,
    MIN_KELVIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luke Roberts light from a config entry."""
    api: LukeRobertsApi = hass.data[DOMAIN][config_entry.entry_id]
    device_name = config_entry.data[CONF_DEVICE_NAME]

    async_add_entities([LukeRobertsLight(api, device_name, config_entry.entry_id)])


class LukeRobertsLight(LightEntity):
    """Representation of a Luke Roberts Model F lamp."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, api: LukeRobertsApi, device_name: str, entry_id: str) -> None:
        """Initialize the light."""
        self._api = api
        self._device_name = device_name
        self._entry_id = entry_id

        # State attributes
        self._attr_is_on = False
        self._attr_brightness: int | None = None
        self._attr_color_temp_kelvin: int | None = None
        self._attr_hs_color: tuple[float, float] | None = None

        # Supported features
        self._attr_supported_color_modes = {
            ColorMode.COLOR_TEMP,
            ColorMode.HS,
        }
        self._attr_color_mode = ColorMode.COLOR_TEMP

        # Color temperature range
        self._attr_min_color_temp_kelvin = MIN_KELVIN
        self._attr_max_color_temp_kelvin = MAX_KELVIN

        # Unique ID
        self._attr_unique_id = f"{device_name}_light"

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_name)},
            "name": device_name,
            "manufacturer": "Luke Roberts",
            "model": "Model F",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        _LOGGER.debug("Turning on light with kwargs: %s", kwargs)

        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
        hs_color = kwargs.get(ATTR_HS_COLOR)

        try:
            # Turn on the lamp
            await self._api.turn_on()
            self._attr_is_on = True

            # Handle brightness
            if brightness is not None:
                # Convert from Home Assistant range (0-255) to lamp range (0-100)
                lamp_brightness = int((brightness / 255) * MAX_BRIGHTNESS)
                await self._api.set_brightness(lamp_brightness)
                self._attr_brightness = brightness

            # Handle color temperature
            if color_temp_kelvin is not None:
                # Ensure it's within range
                kelvin = max(
                    MIN_KELVIN, min(MAX_KELVIN, int(color_temp_kelvin))
                )
                await self._api.set_color_temp_kelvin(kelvin)
                self._attr_color_temp_kelvin = kelvin
                self._attr_color_mode = ColorMode.COLOR_TEMP
                self._attr_hs_color = None

            # Handle color (HS color)
            elif hs_color is not None:
                hue, saturation = hs_color
                # Convert to values for the lamp
                # HS: hue is 0-360, saturation is 0-100
                lamp_hue = int(hue)
                lamp_saturation = int(saturation)

                # Use uplight for color
                lamp_brightness_val = (
                    int((self._attr_brightness / 255) * MAX_BRIGHTNESS)
                    if self._attr_brightness is not None
                    else MAX_BRIGHTNESS
                )
                await self._api.set_uplight(
                    brightness=lamp_brightness_val,
                    hue=lamp_hue,
                    saturation=lamp_saturation,
                )
                self._attr_hs_color = hs_color
                self._attr_color_mode = ColorMode.HS
                self._attr_color_temp_kelvin = None

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error turning on light: %s", err)
            raise

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        _LOGGER.debug("Turning off light")

        try:
            await self._api.turn_off()
            self._attr_is_on = False
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error turning off light: %s", err)
            raise

        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the light."""
        _LOGGER.debug("Updating light state")

        try:
            state = await self._api.get_state()
            _LOGGER.debug("Received state: %s", state)

            # Parse the state response
            # The actual response format may vary, adjust as needed
            if isinstance(state, dict):
                power = state.get("POWER", "").upper()
                self._attr_is_on = power == "ON"

                # Try to get brightness
                if "Dimmer" in state:
                    lamp_brightness = int(state["Dimmer"])
                    # Convert from lamp range (0-100) to HA range (0-255)
                    self._attr_brightness = int(
                        (lamp_brightness / MAX_BRIGHTNESS) * 255
                    )

                # Try to get color temp
                if "CT" in state:
                    ct_mired = int(state["CT"])
                    # Convert mireds to kelvin: K = 1000000 / mireds
                    self._attr_color_temp_kelvin = int(1000000 / ct_mired)

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error updating light state: %s", err)
