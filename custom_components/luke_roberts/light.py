"""Light platform for Luke Roberts integration."""
from __future__ import annotations

from datetime import timedelta
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
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_BRIGHTNESS,
    MAX_KELVIN,
    MAX_SCENE,
    MIN_BRIGHTNESS,
    MIN_KELVIN,
    MIN_SCENE,
)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

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
    _attr_should_poll = True

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
                        # Send scene command reliably (twice with delay)
                        await self._api.send_command_reliable({"scene": scene_num})
                        self._attr_effect = effect
                        self._attr_is_on = True
                        _LOGGER.debug("Set scene %s for lamp %s", scene_num, self._lamp_id)
                        self.async_write_ha_state()
                        return
                    else:
                        _LOGGER.warning("Scene number %s out of range", scene_num)
                except (ValueError, IndexError):
                    _LOGGER.error("Invalid effect format: %s", effect)

            # IMPORTANT: The Luke Roberts Cloud API does NOT work properly with combined commands.
            # Commands with multiple parameters cause unpredictable behavior (random scenes, wrong colors).
            # SOLUTION: Send each parameter as a SEPARATE command with delays between them.
            #
            # Based on extensive testing:
            # - Single parameter commands work reliably and produce reproducible results
            # - Each command must be sent TWICE (first establishes BLE connection, second reaches lamp)
            # - Use 2 second delay between the two sends
            #
            # OPTIMIZATION: Only send commands for parameters that actually change
            # This reduces flickering when adjusting brightness/kelvin on an already-on lamp

            # Step 1: Turn on power (only if lamp is currently off)
            if not self._attr_is_on:
                _LOGGER.debug("Sending power ON command")
                await self._api.send_command_reliable({"power": "ON"})

            # Step 2: Set brightness (only if it changed)
            brightness = kwargs.get(ATTR_BRIGHTNESS)
            if brightness is not None:
                lamp_brightness = int((brightness / 255) * MAX_BRIGHTNESS)
                # Only send if brightness actually changed
                if self._attr_brightness != brightness:
                    _LOGGER.debug("Sending brightness command: %s", lamp_brightness)
                    await self._api.send_command_reliable({"brightness": lamp_brightness})
                self._attr_brightness = brightness
            elif not self._attr_is_on:
                # Lamp was off, set default brightness
                lamp_brightness = 100
                _LOGGER.debug("Sending default brightness command: %s", lamp_brightness)
                await self._api.send_command_reliable({"brightness": lamp_brightness})
                self._attr_brightness = 255

            # Step 3: Set color temperature (only if it changed)
            color_temp_kelvin = kwargs.get(ATTR_COLOR_TEMP_KELVIN)
            if color_temp_kelvin is not None:
                kelvin = max(MIN_KELVIN, min(MAX_KELVIN, int(color_temp_kelvin)))
                # Only send if kelvin actually changed
                if self._attr_color_temp_kelvin != kelvin:
                    _LOGGER.debug("Sending kelvin command: %s", kelvin)
                    await self._api.send_command_reliable({"kelvin": kelvin})
                self._attr_color_temp_kelvin = kelvin
            elif not self._attr_is_on:
                # Lamp was off, set default kelvin
                kelvin = 3000
                _LOGGER.debug("Sending default kelvin command: %s", kelvin)
                await self._api.send_command_reliable({"kelvin": kelvin})
                self._attr_color_temp_kelvin = kelvin

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
            # Send power OFF command reliably (twice with delay)
            await self._api.send_command_reliable({"power": "OFF"})
            self._attr_is_on = False
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error turning off light %s: %s", self._lamp_id, err)
            raise

        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the light.

        The Luke Roberts Cloud API returns state in this format:
        {
            "on": true,
            "online": true,
            "brightness": 2,
            "color": {
                "temperatureK": 2700
            },
            "updated_at": "2026-01-19T14:21:58.771Z"
        }
        """
        _LOGGER.debug("Updating light state for lamp %s", self._lamp_id)

        try:
            state = await self._api.get_state()
            _LOGGER.debug("Received state for lamp %s: %s", self._lamp_id, state)

            if isinstance(state, dict):
                # Power state
                if "on" in state:
                    self._attr_is_on = bool(state["on"])

                # Brightness (0-100 from API, convert to 0-255 for HA)
                if "brightness" in state:
                    lamp_brightness = int(state["brightness"])
                    if lamp_brightness > 0:
                        self._attr_brightness = int((lamp_brightness / MAX_BRIGHTNESS) * 255)
                        # Ensure minimum brightness of 1 in HA (0 means off)
                        if self._attr_brightness == 0:
                            self._attr_brightness = 1

                # Color temperature
                if "color" in state and isinstance(state["color"], dict):
                    if "temperatureK" in state["color"]:
                        kelvin = int(state["color"]["temperatureK"])
                        # Clamp to supported range
                        self._attr_color_temp_kelvin = max(MIN_KELVIN, min(MAX_KELVIN, kelvin))
                        self._attr_color_mode = ColorMode.COLOR_TEMP

                # Log if lamp is offline
                if "online" in state and not state["online"]:
                    _LOGGER.warning("Lamp %s is offline", self._lamp_id)

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error updating light state for lamp %s: %s", self._lamp_id, err)
