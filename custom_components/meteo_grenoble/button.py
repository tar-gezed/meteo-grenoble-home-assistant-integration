"""Button platform for Météo-Grenoble.com."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MeteoGrenobleConfigEntry
from .const import DOMAIN
from .entity import MeteoGrenobleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoGrenobleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Météo-Grenoble.com button platform."""
    coordinator = entry.runtime_data
    async_add_entities([MeteoGrenobleRefreshButton(coordinator, entry)])


class MeteoGrenobleRefreshButton(MeteoGrenobleEntity, ButtonEntity):
    """Button to manually refresh Météo-Grenoble data."""

    def __init__(self, coordinator, entry: MeteoGrenobleConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator, entry)
        self._attr_name = "Actualiser"
        self._attr_icon = "mdi:refresh"
        self._attr_unique_id = f"{DOMAIN}_refresh"

    async def async_press(self) -> None:
        """Press the button to refresh data."""
        await self.coordinator.async_request_refresh()
