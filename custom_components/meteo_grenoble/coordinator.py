"""DataUpdateCoordinator for the Météo-Grenoble.com integration."""
from __future__ import annotations

import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, HEADERS, LOGGER, UPDATE_INTERVAL, URL_METEO_GRENOBLE
from .parser import parse_rsc_stream


class MeteoGrenobleDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Météo-Grenoble.com weather data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict:
        """Fetch data from the Météo-Grenoble.com Next.js RSC endpoint."""
        try:
            async with async_timeout.timeout(15):
                response = await self.session.get(
                    URL_METEO_GRENOBLE,
                    headers=HEADERS,
                    raise_for_status=True,
                )
                content = await response.text()
                return parse_rsc_stream(content)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with server: {err}") from err
