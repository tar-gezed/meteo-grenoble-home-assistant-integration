"""Constants for the Météo-Grenoble.com integration."""
from datetime import timedelta
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "meteo_grenoble"
DEFAULT_NAME = "Météo-Grenoble.com"

URL_METEO_GRENOBLE = "https://www.meteo-grenoble.com/"

HEADERS = {
    "User-Agent": "HomeAssistant/MeteoGrenoble/1.0.7",
    "RSC": "1",
}

UPDATE_INTERVAL = timedelta(minutes=18)

from homeassistant.const import Platform
PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR, Platform.BINARY_SENSOR]
