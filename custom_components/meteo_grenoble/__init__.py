"""The Météo-Grenoble.com integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import MeteoGrenobleDataUpdateCoordinator

type MeteoGrenobleConfigEntry = ConfigEntry[MeteoGrenobleDataUpdateCoordinator]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: MeteoGrenobleConfigEntry) -> bool:
    """Set up Météo-Grenoble.com from a config entry."""
    coordinator = MeteoGrenobleDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: MeteoGrenobleConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
