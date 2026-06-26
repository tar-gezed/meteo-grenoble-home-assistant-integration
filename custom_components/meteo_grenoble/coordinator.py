"""DataUpdateCoordinator for the Météo-Grenoble.com integration."""
from __future__ import annotations

from asyncio import timeout
from typing import Any, TypedDict

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, HEADERS, LOGGER, UPDATE_INTERVAL, URL_METEO_GRENOBLE
from .parser import parse_rsc_stream


class MeteoGrenobleData(TypedDict):
    realtime: dict[str, Any]
    forecasts: list[dict[str, Any]]
    rain: list[dict[str, Any]]


class MeteoGrenobleDataUpdateCoordinator(DataUpdateCoordinator[MeteoGrenobleData]):
    """Class to manage fetching Météo-Grenoble.com weather data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self) -> MeteoGrenobleData:
        """Fetch data from the Météo-Grenoble.com Next.js RSC endpoint."""
        try:
            async with timeout(15):
                response = await self.session.get(
                    URL_METEO_GRENOBLE,
                    headers=HEADERS,
                    raise_for_status=True,
                )
                content = await response.text()
                return await self.hass.async_add_executor_job(parse_rsc_stream, content)
        except (TimeoutError, aiohttp.ClientError) as err:
            if self.data and isinstance(self.data, dict) and "realtime" in self.data:
                LOGGER.warning(
                    "Network error fetching meteo_grenoble data, using previous cached data: %s",
                    err,
                )
                return self.data
            raise UpdateFailed(f"Network error communicating with server: {err}") from err
        except ValueError as err:
            LOGGER.debug("Failed to parse RSC stream content: %s", content)
            raise UpdateFailed(f"Parsing error: {err}") from err

