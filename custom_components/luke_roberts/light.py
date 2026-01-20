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
    CONF_SCENE_NAMES,
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

    async_add_entities([LukeRobertsLight(api, device_name, lamp_id, config_entry)])


class LukeRobertsLight(LightEntity):
    """Representation of a Luke Roberts Model F lamp."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = True

    def __init__(self, api: LukeRobertsApi, device_name: str, lamp_id: int, config_entry: ConfigEntry) -> None:
        """Initialize the light."""
        self._api = api
        self._device_name = device_name
        self._lamp_id = lamp_id
        self._config_entry = config_entry

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
        # Get custom scene names from options, or use defaults
        custom_scene_names = config_entry.options.get(CONF_SCENE_NAMES, {})
        self._attr_effect_list = []
        for i in range(MIN_SCENE + 1, MAX_SCENE + 1):
            scene_name = custom_scene_names.get(str(i), f"Scene {i}")
            self._attr_effect_list.append(scene_name)
        self._attr_effect: str | None = None
        # Store mapping for reverse lookup (scene name -> scene number)
        self._scene_name_to_num = {name: i for i, name in enumerate(self._attr_effect_list, start=MIN_SCENE + 1)}

        # Unique ID
        self._attr_unique_id = f"luke_roberts_{lamp_id}_light"

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(lamp_id))},
            "name": device_name,
            "manufacturer": "Luke Roberts",
            "model": "Model F",
        }

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass - fetch initial state."""
        await super().async_added_to_hass()

        # Listen for options updates to refresh scene names
        self._config_entry.async_on_unload(
            self._config_entry.add_update_listener(self._async_update_listener)
        )

        # Fetch initial state to properly initialize sliders
        await self.async_update()

    async def _async_update_listener(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Handle options update."""
        # Update scene names from new options
        custom_scene_names = entry.options.get(CONF_SCENE_NAMES, {})
        self._attr_effect_list = []
        for i in range(MIN_SCENE + 1, MAX_SCENE + 1):
            scene_name = custom_scene_names.get(str(i), f"Scene {i}")
            self._attr_effect_list.append(scene_name)
        # Update mapping
        self._scene_name_to_num = {name: i for i, name in enumerate(self._attr_effect_list, start=MIN_SCENE + 1)}
        # Update state
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        _LOGGER.debug("Turning on light %s with kwargs: %s", self._lamp_id, kwargs)

        try:
            # Handle scene/effect selection separately
            effect = kwargs.get(ATTR_EFFECT)
            if effect is not None:
                # Scenes are a separate command type
                try:
                    # Look up scene number from scene name
                    scene_num = self._scene_name_to_num.get(effect)
                    if scene_num is None:
                        # Fallback: try to parse as "Scene X" format
                        scene_num = int(effect.split()[-1])

                    if MIN_SCENE <= scene_num <= MAX_SCENE:
                        # Send scene command (twice with delay for BLE bridge)
                        await self._api.send_command_reliable({"scene": scene_num})
                        self._attr_effect = effect
                        self._attr_is_on = True
                        _LOGGER.debug("Set scene %s (%s) for lamp %s", effect, scene_num, self._lamp_id)
                        self.async_write_ha_state()
                        return
                    else:
                        _LOGGER.warning("Scene number %s out of range", scene_num)
                except (ValueError, IndexError, TypeError):
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
                # Progressive brightness scaling for better control:
                # - 0-70% HA (0-179): maps to 0-50% API (fine control in normal range)
                # - 70-100% HA (179-255): maps to 50-100% API (steeper, access to full brightness)
                # This gives fine control where needed while allowing full brightness

                if brightness <= 179:  # 0-70% range
                    # Linear mapping: 0-179 HA → 0-50 API
                    lamp_brightness = int((brightness / 179) * 50)
                else:  # 70-100% range
                    # Linear mapping: 179-255 HA → 50-100 API
                    lamp_brightness = int(50 + ((brightness - 179) / 76) * 50)

                # Only send if brightness actually changed
                if self._attr_brightness != brightness:
                    _LOGGER.debug("Sending brightness command: %s (HA: %s)", lamp_brightness, brightness)
                    await self._api.send_command_reliable({"brightness": lamp_brightness})
                self._attr_brightness = brightness
            elif not self._attr_is_on:
                # Lamp was off, set default brightness (50% HA = ~28% API)
                lamp_brightness = 28
                _LOGGER.debug("Sending default brightness command: %s", lamp_brightness)
                await self._api.send_command_reliable({"brightness": lamp_brightness})
                self._attr_brightness = 128  # 50% in HA

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

        # Schedule immediate update after state is written
        # This ensures UI shows correct values right after command completes
        self.async_schedule_update_ha_state(force_refresh=True)

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

        # Schedule immediate update after state is written
        self.async_schedule_update_ha_state(force_refresh=True)

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

                # Brightness: Reverse progressive scaling
                # - 0-50% API (0-50): maps to 0-70% HA (0-179)
                # - 50-100% API (50-100): maps to 70-100% HA (179-255)
                if "brightness" in state:
                    lamp_brightness = int(state["brightness"])
                    if lamp_brightness > 0:
                        if lamp_brightness <= 50:  # 0-50% API range
                            # Reverse mapping: 0-50 API → 0-179 HA
                            self._attr_brightness = int((lamp_brightness / 50) * 179)
                        else:  # 50-100% API range
                            # Reverse mapping: 50-100 API → 179-255 HA
                            self._attr_brightness = int(179 + ((lamp_brightness - 50) / 50) * 76)

                        # Ensure minimum brightness of 1 in HA (0 means off)
                        if self._attr_brightness == 0:
                            self._attr_brightness = 1
                        # Cap at 255 just in case
                        if self._attr_brightness > 255:
                            self._attr_brightness = 255

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
