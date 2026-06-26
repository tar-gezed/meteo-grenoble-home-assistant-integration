"""Binary sensor platform for Météo-Grenoble.com."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .__init__ import MeteoGrenobleConfigEntry
from .const import DOMAIN
from .entity import MeteoGrenobleEntity
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
    entry: MeteoGrenobleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Météo-Grenoble.com binary sensor platform."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            MeteoGrenobleBinarySensor(coordinator, entry, description)
            for description in BINARY_SENSOR_TYPES
        ],
        True,
    )


class MeteoGrenobleBinarySensor(MeteoGrenobleEntity, BinarySensorEntity):
    """Representation of a Météo-Grenoble.com vigilance binary sensor."""

    def __init__(
        self, coordinator, entry: MeteoGrenobleConfigEntry, description: BinarySensorEntityDescription
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_vigilance_{description.key}"

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
