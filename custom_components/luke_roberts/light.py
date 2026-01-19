"""Light platform for Luke Roberts integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.color as color_util

from .api import LukeRobertsApi
from .const import (
    CONF_DEVICE_NAME,
    CONF_LAMP_ID,
    DOMAIN,
    MAX_BRIGHTNESS,
    MAX_KELVIN,
    MAX_SCENE,
    MIN_BRIGHTNESS,
    MIN_KELVIN,
    MIN_SCENE,
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
    lamp_id = config_entry.data[CONF_LAMP_ID]

    async_add_entities([LukeRobertsLight(api, device_name, lamp_id, config_entry.entry_id)])


class LukeRobertsLight(LightEntity):
    """Representation of a Luke Roberts Model F lamp."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, api: LukeRobertsApi, device_name: str, lamp_id: int, entry_id: str) -> None:
        """Initialize the light."""
        self._api = api
        self._device_name = device_name
        self._lamp_id = lamp_id
        self._entry_id = entry_id

        # State attributes
        self._attr_is_on = False
        self._attr_brightness: int | None = None
        self._attr_color_temp_kelvin: int | None = None
        self._attr_hs_color: tuple[float, float] | None = None
        self._attr_rgb_color: tuple[int, int, int] | None = None

        # Supported features
        # Note: RGB/HS modes are experimental - official API may only support COLOR_TEMP
        # Based on https://github.com/denniedegroot/com.luke.roberts
        self._attr_supported_color_modes = {
            ColorMode.COLOR_TEMP,
            # ColorMode.HS,  # May not be supported by Cloud API
            # ColorMode.RGB,  # May not be supported by Cloud API
        }
        self._attr_color_mode = ColorMode.COLOR_TEMP

        # Color temperature range
        self._attr_min_color_temp_kelvin = MIN_KELVIN
        self._attr_max_color_temp_kelvin = MAX_KELVIN

        # Scene/Effect support
        self._attr_supported_features = LightEntityFeature.EFFECT
        # Scenes 1-31 (Scene 0 = Off, which is handled by power)
        self._attr_effect_list = [f"Scene {i}" for i in range(MIN_SCENE + 1, MAX_SCENE + 1)]
        self._attr_effect: str | None = None

        # Unique ID
        self._attr_unique_id = f"luke_roberts_{lamp_id}_light"

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(lamp_id))},
            "name": device_name,
            "manufacturer": "Luke Roberts",
            "model": "Model F",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        _LOGGER.debug("Turning on light %s with kwargs: %s", self._lamp_id, kwargs)

        try:
            # Handle scene/effect selection separately
            effect = kwargs.get(ATTR_EFFECT)
            if effect is not None:
                # Scenes are a separate command type
                try:
                    scene_num = int(effect.split()[-1])
                    if MIN_SCENE <= scene_num <= MAX_SCENE:
                        await self._api.set_scene(scene_num)
                        self._attr_effect = effect
                        self._attr_is_on = True
                        _LOGGER.debug("Set scene %s for lamp %s", scene_num, self._lamp_id)
                        self.async_write_ha_state()
                        return
                    else:
                        _LOGGER.warning("Scene number %s out of range", scene_num)
                except (ValueError, IndexError):
                    _LOGGER.error("Invalid effect format: %s", effect)

            # Build combined command for brightness and color temperature
            # Use simple brightness/kelvin parameters (not downlight/uplight)
            # This provides the correct behavior for standard white light

            command = {"power": "ON"}

            # Get brightness
            brightness = kwargs.get(ATTR_BRIGHTNESS)
            if brightness is not None:
                lamp_brightness = int((brightness / 255) * MAX_BRIGHTNESS)
                self._attr_brightness = brightness
            else:
                lamp_brightness = int((self._attr_brightness / 255) * MAX_BRIGHTNESS) if self._attr_brightness else 100

            command["brightness"] = lamp_brightness

            # Get color temperature
            color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
            if color_temp_kelvin is not None:
                kelvin = max(MIN_KELVIN, min(MAX_KELVIN, int(color_temp_kelvin)))
                self._attr_color_temp_kelvin = kelvin
            else:
                kelvin = self._attr_color_temp_kelvin if self._attr_color_temp_kelvin else 3000

            command["kelvin"] = kelvin

            # Send combined command
            _LOGGER.debug("Sending combined command: %s", command)
            await self._api.send_command(command)

            self._attr_is_on = True
            self._attr_color_mode = ColorMode.COLOR_TEMP
            self._attr_hs_color = None
            self._attr_rgb_color = None

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error turning on light %s: %s", self._lamp_id, err)
            raise

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        _LOGGER.debug("Turning off light %s", self._lamp_id)

        try:
            await self._api.turn_off()
            self._attr_is_on = False
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error turning off light %s: %s", self._lamp_id, err)
            raise

        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the light."""
        _LOGGER.debug("Updating light state for lamp %s", self._lamp_id)

        try:
            state = await self._api.get_state()
            _LOGGER.debug("Received state for lamp %s: %s", self._lamp_id, state)

            # Parse the state response
            # The actual response format may vary based on what the API returns
            if isinstance(state, dict):
                # Check for power state
                if "power" in state:
                    power = str(state["power"]).upper()
                    self._attr_is_on = power in ["ON", "TRUE", "1"]
                elif "state" in state:
                    power = str(state["state"]).upper()
                    self._attr_is_on = power in ["ON", "TRUE", "1"]

                # Try to get brightness
                if "brightness" in state:
                    lamp_brightness = int(state["brightness"])
                    # Convert from lamp range (0-100) to HA range (0-255)
                    self._attr_brightness = int((lamp_brightness / MAX_BRIGHTNESS) * 255)

                # Try to get color temp
                if "color_temperature" in state:
                    self._attr_color_temp_kelvin = int(state["color_temperature"])
                    self._attr_color_mode = ColorMode.COLOR_TEMP

                # Try to get RGB color
                if "red" in state and "green" in state and "blue" in state:
                    red = int(state["red"])
                    green = int(state["green"])
                    blue = int(state["blue"])
                    self._attr_rgb_color = (red, green, blue)
                    self._attr_hs_color = color_util.color_RGB_to_hs(red, green, blue)
                    self._attr_color_mode = ColorMode.RGB

                # Try to get HSV color
                elif "hue" in state and "saturation" in state:
                    hue = float(state["hue"])
                    saturation = float(state["saturation"])
                    self._attr_hs_color = (hue, saturation)
                    self._attr_rgb_color = color_util.color_hs_to_RGB(hue, saturation)
                    self._attr_color_mode = ColorMode.HS

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error updating light state for lamp %s: %s", self._lamp_id, err)
