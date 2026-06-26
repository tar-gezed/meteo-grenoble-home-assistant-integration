"""Base entity class for Météo-Grenoble.com."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN


class MeteoGrenobleEntity(CoordinatorEntity):
    """Base class for Météo-Grenoble.com entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name=DEFAULT_NAME,
            manufacturer="Météo Grenoble",
            model="meteo-grenoble.com",
            entry_type=DeviceEntryType.SERVICE,
        )
