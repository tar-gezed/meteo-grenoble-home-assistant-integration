"""Binary sensor platform for Météo-Grenoble.com."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .parser import get_today_forecast

# Description of all binary sensors (vigilances)
BINARY_SENSOR_TYPES: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="highTemperature",
        name="Vigilance Canicule",
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    BinarySensorEntityDescription(
        key="snow",
        name="Vigilance Neige",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    BinarySensorEntityDescription(
        key="freezingRain",
        name="Vigilance Verglas",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    BinarySensorEntityDescription(
        key="storm",
        name="Vigilance Orage",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    BinarySensorEntityDescription(
        key="strongWind",
        name="Vigilance Vent Fort",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    BinarySensorEntityDescription(
        key="permanentFrost",
        name="Vigilance Grand Froid",
        device_class=BinarySensorDeviceClass.COLD,
    ),
    BinarySensorEntityDescription(
        key="heavyRain",
        name="Vigilance Pluie Inondation",
        device_class=BinarySensorDeviceClass.MOISTURE,
    ),
    BinarySensorEntityDescription(
        key="frost",
        name="Vigilance Gel",
        device_class=BinarySensorDeviceClass.COLD,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Météo-Grenoble.com binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MeteoGrenobleBinarySensor(coordinator, entry, description)
            for description in BINARY_SENSOR_TYPES
        ],
        True,
    )


class MeteoGrenobleBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Météo-Grenoble.com vigilance binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator, entry: ConfigEntry, description: BinarySensorEntityDescription
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_vigilance_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer="Météo Grenoble",
            model="meteo-grenoble.com",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        key = self.entity_description.key
        forecasts = self.coordinator.data.get("forecasts", [])
        if not forecasts:
            return None

        today = get_today_forecast(forecasts)
        if not today:
            return None
        vigilances = today.get("vigilances", {})
        val = vigilances.get(key)
        return bool(val) if val is not None else False
