"""API client for Luke Roberts lamps."""
import asyncio
import json
import logging
from typing import Any

import aiohttp

from .const import (
    API_PATH,
    CMD_CT,
    CMD_DIMMER,
    CMD_DOWNLIGHT,
    CMD_KELVIN,
    CMD_POWER,
    CMD_STATE,
    CMD_UPLIGHT,
    DEFAULT_PORT,
    STATE_OFF,
    STATE_ON,
)

_LOGGER = logging.getLogger(__name__)


class LukeRobertsApi:
    """API client for Luke Roberts lamp."""

    def __init__(self, host: str, device_name: str, port: int = DEFAULT_PORT) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.device_name = device_name
        self._session: aiohttp.ClientSession | None = None

    def _get_url(self, command: str, params: str = "") -> str:
        """Build the API URL."""
        base_url = f"http://{self.host}:{self.port}{API_PATH}"
        if params:
            return f"{base_url}?cmnd={command}%20{params}"
        return f"{base_url}?cmnd={command}"

    async def _request(self, command: str, params: str = "") -> dict[str, Any]:
        """Send a request to the lamp."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        url = self._get_url(command, params)
        _LOGGER.debug("Requesting URL: %s", url)

        try:
            async with asyncio.timeout(10):
                async with self._session.get(url) as response:
                    response.raise_for_status()
                    text = await response.text()
                    _LOGGER.debug("Response: %s", text)

                    # Try to parse JSON response
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        # If not JSON, return as plain text
                        return {"response": text}
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout connecting to lamp at %s", self.host)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to lamp: %s", err)
            raise

    async def close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def turn_on(self) -> dict[str, Any]:
        """Turn the lamp on."""
        return await self._request(CMD_POWER, STATE_ON)

    async def turn_off(self) -> dict[str, Any]:
        """Turn the lamp off."""
        return await self._request(CMD_POWER, STATE_OFF)

    async def set_brightness(self, brightness: int) -> dict[str, Any]:
        """Set the brightness (0-100)."""
        return await self._request(CMD_DIMMER, str(brightness))

    async def set_color_temp_kelvin(self, kelvin: int) -> dict[str, Any]:
        """Set the color temperature in Kelvin (2700-4000)."""
        return await self._request(CMD_KELVIN, str(kelvin))

    async def set_color_temp_mired(self, mired: int) -> dict[str, Any]:
        """Set the color temperature in mireds (250-416)."""
        return await self._request(CMD_CT, str(mired))

    async def set_uplight(
        self,
        brightness: int | None = None,
        hue: int | None = None,
        saturation: int | None = None,
        duration: int = 0,
    ) -> dict[str, Any]:
        """Set uplight parameters."""
        params = {"duration": duration}
        if brightness is not None:
            params["brightness"] = brightness
        if hue is not None:
            params["hue"] = hue
        if saturation is not None:
            params["saturation"] = saturation

        json_params = json.dumps(params)
        return await self._request(CMD_UPLIGHT, json_params)

    async def set_downlight(
        self,
        brightness: int | None = None,
        kelvin: int | None = None,
        ct: int | None = None,
        saturation: int | None = None,
        duration: int = 0,
    ) -> dict[str, Any]:
        """Set downlight parameters."""
        params = {"duration": duration}
        if brightness is not None:
            params["brightness"] = brightness
        if kelvin is not None:
            params["kelvin"] = kelvin
        if ct is not None:
            params["ct"] = ct
        if saturation is not None:
            params["saturation"] = saturation

        json_params = json.dumps(params)
        return await self._request(CMD_DOWNLIGHT, json_params)

    async def get_state(self) -> dict[str, Any]:
        """Get the current state of the lamp."""
        return await self._request(CMD_STATE)

    async def test_connection(self) -> bool:
        """Test if we can connect to the lamp."""
        try:
            await self.get_state()
            return True
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Connection test failed: %s", err)
            return False
