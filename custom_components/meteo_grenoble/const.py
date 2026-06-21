"""Constants for the Météo-Grenoble.com integration."""
from datetime import timedelta
import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "meteo_grenoble"
DEFAULT_NAME = "Météo-Grenoble.com"

URL_METEO_GRENOBLE = "https://www.meteo-grenoble.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "RSC": "1",
}

UPDATE_INTERVAL = timedelta(minutes=15)

PLATFORMS = ["weather", "sensor", "binary_sensor"]
