"""API client for Luke Roberts Cloud API."""
import asyncio
import logging
from typing import Any

import aiohttp

from .const import (
    API_BASE_URL,
    API_TIMEOUT,
    ENDPOINT_LAMP_COMMAND,
    ENDPOINT_LAMP_STATE,
    ENDPOINT_LAMPS,
    STATE_OFF,
    STATE_ON,
)

_LOGGER = logging.getLogger(__name__)


class LukeRobertsApiError(Exception):
    """Base exception for Luke Roberts API errors."""


class LukeRobertsAuthError(LukeRobertsApiError):
    """Authentication error."""


class LukeRobertsConnectionError(LukeRobertsApiError):
    """Connection error."""


class LukeRobertsApi:
    """API client for Luke Roberts Cloud API."""

    def __init__(self, api_token: str, lamp_id: int) -> None:
        """Initialize the API client."""
        self.api_token = api_token
        self.lamp_id = lamp_id
        self._session: aiohttp.ClientSession | None = None
        self._headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint: str) -> str:
        """Build the API URL."""
        endpoint = endpoint.replace("{lamp_id}", str(self.lamp_id))
        return f"{API_BASE_URL}{endpoint}"

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have an active session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """Send a request to the Luke Roberts Cloud API."""
        session = await self._ensure_session()
        url = self._get_url(endpoint)

        _LOGGER.debug(
            "API Request: %s %s with data: %s",
            method,
            url,
            json_data if json_data else "None",
        )

        try:
            async with asyncio.timeout(API_TIMEOUT):
                async with session.request(
                    method,
                    url,
                    headers=self._headers,
                    json=json_data,
                ) as response:
                    response_text = await response.text()
                    _LOGGER.debug(
                        "API Response [%s]: %s", response.status, response_text
                    )

                    if response.status == 401:
                        raise LukeRobertsAuthError("Invalid API token")
                    if response.status == 404:
                        raise LukeRobertsApiError(f"Lamp {self.lamp_id} not found")

                    response.raise_for_status()

                    # Try to parse JSON response
                    try:
                        return await response.json()
                    except Exception:  # noqa: BLE001
                        # Some endpoints return plain text
                        return response_text

        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to Luke Roberts Cloud API")
            raise LukeRobertsConnectionError("API request timeout") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Luke Roberts Cloud API: %s", err)
            raise LukeRobertsConnectionError(str(err)) from err

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_lamps(self) -> list[dict[str, Any]]:
        """Get all lamps."""
        result = await self._request("GET", ENDPOINT_LAMPS)
        if isinstance(result, list):
            return result
        return []

    async def get_state(self) -> dict[str, Any]:
        """Get the current state of the lamp."""
        result = await self._request("GET", ENDPOINT_LAMP_STATE)
        if isinstance(result, str):
            # If the API returns a string, try to parse it or return as dict
            return {"raw_state": result}
        return result

    async def send_command(self, command: dict[str, Any]) -> dict[str, Any] | str:
        """Send a command to the lamp."""
        return await self._request("PUT", ENDPOINT_LAMP_COMMAND, command)

    async def turn_on(self) -> dict[str, Any] | str:
        """Turn the lamp on."""
        return await self.send_command({"power": STATE_ON})

    async def turn_off(self) -> dict[str, Any] | str:
        """Turn the lamp off."""
        return await self.send_command({"power": STATE_OFF})

    async def set_brightness(
        self, brightness: int, relative: bool = False
    ) -> dict[str, Any] | str:
        """Set the brightness (0-100)."""
        return await self.send_command({"brightness": brightness, "relative": relative})

    async def set_scene(self, scene: int) -> dict[str, Any] | str:
        """Set a scene."""
        return await self.send_command({"scene": scene})

    async def set_color_temp_kelvin(self, kelvin: int) -> dict[str, Any] | str:
        """Set the color temperature in Kelvin."""
        # Based on typical Luke Roberts API, try these parameter names
        # We'll try multiple approaches as the API docs don't specify this
        return await self.send_command({"color_temperature": kelvin})

    async def set_color_hsv(
        self, hue: int, saturation: int, value: int | None = None
    ) -> dict[str, Any] | str:
        """Set color using HSV values."""
        command = {"hue": hue, "saturation": saturation}
        if value is not None:
            command["value"] = value
        return await self.send_command(command)

    async def set_color_rgb(self, red: int, green: int, blue: int) -> dict[str, Any] | str:
        """Set color using RGB values (0-255)."""
        return await self.send_command({"red": red, "green": green, "blue": blue})

    async def test_connection(self) -> bool:
        """Test if we can connect to the API."""
        try:
            await self.get_state()
            return True
        except LukeRobertsAuthError:
            _LOGGER.error("Authentication failed - invalid API token")
            return False
        except LukeRobertsApiError as err:
            _LOGGER.error("API error during connection test: %s", err)
            return False
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Connection test failed: %s", err)
            return False
