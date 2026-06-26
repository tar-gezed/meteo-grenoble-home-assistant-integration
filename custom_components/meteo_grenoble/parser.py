"""Parser for the Next.js RSC weather data stream from Météo-Grenoble.com."""
import base64
import json
import logging
import re
from typing import Any

from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


def decode_content(content: str) -> str:
    """Try to decode the content if it's base64 encoded."""
    try:
        # Base64 string from Next.js might have surrounding whitespace
        clean_content = content.strip()
        # validate=True ensures it strictly follows base64 encoding
        decoded = base64.b64decode(clean_content, validate=True)
        return decoded.decode("utf-8")
    except Exception:
        # If decoding fails, it is not valid base64, return original content
        return content


def parse_rsc_stream(content: str) -> dict[str, Any]:
    """Parse the raw Next.js RSC text stream and extract weather components."""
    if not content or not content.strip():
        raise ValueError("Empty response received from the server")

    content = decode_content(content)

    forecasts_list: list[list[dict[str, Any]]] = []
    rain_list: list[list[dict[str, Any]]] = []
    realtime_list: list[dict[str, Any]] = []
    flash_alerts: list[dict[str, Any]] = []

    def search_data(obj: Any, depth: int = 0) -> None:
        """Recursively search for target dictionaries in the parsed object."""
        if depth > 50:
            return
            
        if isinstance(obj, str) and (obj.startswith('{') or obj.startswith('[')):
            try:
                parsed_str = json.loads(obj)
                search_data(parsed_str, depth + 1)
            except json.JSONDecodeError:
                pass

        if isinstance(obj, dict):
            # Extract flash alerts
            if "flashTextHtml" in obj and "flashUpdatedAt" in obj:
                flash_alerts.append(obj)

            # Find daily forecasts
            if "forecasts" in obj and isinstance(obj["forecasts"], list):
                f_list = obj["forecasts"]
                if len(f_list) > 0 and isinstance(f_list[0], dict) and "day" in f_list[0]:
                    forecasts_list.append(f_list)

            # Find rain forecast in the hour
            if "rain" in obj and isinstance(obj["rain"], list) and len(obj["rain"]) > 0:
                if isinstance(obj["rain"][0], dict) and "desc" in obj["rain"][0]:
                    rain_list.append(obj["rain"])

            # Find realtime weather data
            if "temperature" in obj and "humidex" in obj and "wind_speed" in obj:
                realtime_list.append(obj)

            # Recurse
            for val in obj.values():
                if isinstance(val, (dict, list, str)):
                    search_data(val, depth + 1)

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list, str)):
                    search_data(item, depth + 1)

    lines = content.split("\n")
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        match = re.match(r'^([0-9a-zA-Z]+):(.*)', cleaned_line)
        if not match:
            continue
            
        val_str = match.group(2)
        
        # Handle Next.js RSC chunk type prefixes (I, T, M, H, L) followed by JSON
        if len(val_str) > 1 and val_str[0] in "ITMHL" and val_str[1] in "[{":
            val_str = val_str[1:]
            
        try:
            obj = json.loads(val_str)
            search_data(obj)
        except json.JSONDecodeError:
            pass

    if not realtime_list and not forecasts_list:
        _LOGGER.error("Weather data structures not found in RSC stream. RSC structure might have changed.")
        raise ValueError("Could not find weather data in the RSC stream")

    if not realtime_list:
        _LOGGER.debug("Realtime data not found in RSC stream.")
    if not forecasts_list:
        _LOGGER.debug("Forecasts data not found in RSC stream.")

    realtime = realtime_list[0] if realtime_list else {}
    forecasts = forecasts_list[0] if forecasts_list else []
    rain = rain_list[0] if rain_list else []

    if flash_alerts:
        flash_alerts.sort(key=lambda x: x.get("flashUpdatedAt", ""), reverse=True)
        latest_flash = flash_alerts[0]
        for day in forecasts:
            if isinstance(day, dict):
                day["flash"] = latest_flash

    _LOGGER.debug("Extracted %d realtime metrics, %d forecast days", len(realtime), len(forecasts))

    return {
        "realtime": realtime,
        "forecasts": forecasts,
        "rain": rain,
    }


def get_today_forecast(forecasts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the forecast dictionary for today in local time."""
    if not forecasts:
        return None
    today = dt_util.now().date()
    for day in forecasts:
        day_str = day.get("day", "")
        if not day_str:
            continue
        try:
            forecast_date = dt_util.parse_datetime(day_str).date()
            if forecast_date == today:
                return day
        except Exception as e:
            _LOGGER.warning("Could not parse forecast date '%s': %s", day_str, e)
    
    _LOGGER.warning("Today's forecast not found, falling back to first available day")
    return forecasts[0]


def get_yesterday_forecast(forecasts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the forecast dictionary for yesterday in local time."""
    if not forecasts:
        return None
    from datetime import timedelta
    yesterday = dt_util.now().date() - timedelta(days=1)
    for day in forecasts:
        day_str = day.get("day", "")
        if not day_str:
            continue
        try:
            forecast_date = dt_util.parse_datetime(day_str).date()
            if forecast_date == yesterday:
                return day
        except Exception as e:
            _LOGGER.warning("Could not parse forecast date '%s' for yesterday: %s", day_str, e)
    return None


def get_flash_alert(forecasts: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the flash alert dictionary from the forecasts list."""
    if not forecasts:
        return None
    for day in forecasts:
        flash = day.get("flash")
        if isinstance(flash, dict):
            return flash
    return None
