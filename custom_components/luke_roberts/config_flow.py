"""Config flow for Luke Roberts integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api import LukeRobertsApi, LukeRobertsAuthError, LukeRobertsApiError
from .const import CONF_API_TOKEN, CONF_DEVICE_NAME, CONF_LAMP_ID, CONF_SCENE_NAMES, DOMAIN, MAX_SCENE, MIN_SCENE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_TOKEN): cv.string,
        vol.Required(CONF_LAMP_ID): cv.positive_int,
        vol.Optional(CONF_DEVICE_NAME): cv.string,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = LukeRobertsApi(
        api_token=data[CONF_API_TOKEN],
        lamp_id=data[CONF_LAMP_ID],
    )

    try:
        # Test connection and get lamp state
        state = await api.get_state()

        # If no device name provided, use lamp ID
        device_name = data.get(CONF_DEVICE_NAME)
        if not device_name:
            device_name = f"Luke Roberts Lamp {data[CONF_LAMP_ID]}"

        await api.close()

        return {
            "title": device_name,
            "lamp_id": data[CONF_LAMP_ID],
        }
    except LukeRobertsAuthError:
        await api.close()
        raise InvalidAuth
    except LukeRobertsApiError as err:
        await api.close()
        _LOGGER.error("API error: %s", err)
        raise CannotConnect
    except Exception as err:
        await api.close()
        _LOGGER.exception("Unexpected exception during validation")
        raise CannotConnect from err


class LukeRobertsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luke Roberts."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return LukeRobertsOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(f"lamp_{info['lamp_id']}")
                self._abort_if_unique_id_configured()

                # Store device name in data
                user_input[CONF_DEVICE_NAME] = info["title"]

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "api_token_help": "Den API Token findest du in deinem Luke Roberts Account",
                "lamp_id_help": "Die Lamp ID findest du in der URL oder API",
            },
        )


class LukeRobertsOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Luke Roberts."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Convert scene_1, scene_2, etc. format to {1: "name", 2: "name", ...}
            scene_names = {}
            for key, value in user_input.items():
                if key.startswith("scene_") and value and value.strip():  # Only save non-empty names
                    scene_num = key.replace("scene_", "")
                    scene_names[scene_num] = value.strip()

            # Save the scene names
            return self.async_create_entry(
                title="",
                data={CONF_SCENE_NAMES: scene_names}
            )

        # Get current scene names or create defaults
        current_scene_names = self.config_entry.options.get(CONF_SCENE_NAMES, {})

        # Build schema for scene name inputs
        # Split into manageable chunks: first 10 scenes to start
        schema_dict = {}

        try:
            for scene_num in range(MIN_SCENE + 1, min(MAX_SCENE + 1, 11)):  # Only scenes 1-10
                default_name = current_scene_names.get(str(scene_num), f"Scene {scene_num}")
                schema_dict[vol.Optional(f"scene_{scene_num}", description=f"Scene {scene_num}", default=default_name)] = str
        except Exception as err:
            _LOGGER.error("Error building schema: %s", err)
            # Fallback to minimal schema
            schema_dict = {
                vol.Optional("scene_1", default="Scene 1"): str,
                vol.Optional("scene_2", default="Scene 2"): str,
                vol.Optional("scene_3", default="Scene 3"): str,
            }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "info": "Customize the names of the first 10 scenes. Leave empty for default name."
            },
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid authentication."""
