"""Tests for the Météo-Grenoble.com data parser."""
import os
import pytest
from datetime import timedelta

from homeassistant.util import dt as dt_util

from custom_components.meteo_grenoble.parser import (
    parse_rsc_stream,
    get_today_forecast,
    get_yesterday_forecast,
    get_flash_alert,
)
from custom_components.meteo_grenoble.picto import (
    map_picto_to_condition,
    map_picto_to_description,
)

# Resolve path to fixture files for tests
FIXTURES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)


def read_scratch_file(filename: str) -> str:
    """Read a fixture file from the local fixtures directory."""
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_parse_empty_stream():
    """Test that parsing an empty stream raises a ValueError."""
    with pytest.raises(ValueError, match="Empty response received"):
        parse_rsc_stream("")

    with pytest.raises(ValueError, match="Empty response received"):
        parse_rsc_stream("   \n   ")


def test_parse_invalid_stream():
    """Test that parsing an invalid stream raises a ValueError."""
    with pytest.raises(ValueError, match="Could not find weather data"):
        parse_rsc_stream("1:I[1, 2, 3]\n2:T[4, 5, 6]")


def test_parse_home_rsc():
    """Test parsing the home_rsc.txt stream (main homepage)."""
    content = read_scratch_file("home_rsc.txt")
    data = parse_rsc_stream(content)

    assert "realtime" in data
    assert "forecasts" in data
    assert "rain" in data

    realtime = data["realtime"]
    forecasts = data["forecasts"]
    rain = data["rain"]

    # Verify realtime structure
    assert isinstance(realtime.get("temperature"), (int, float))
    assert realtime.get("temperature") == 22.3
    assert realtime.get("wind_direction_label") == "Sud-Ouest"
    assert realtime.get("humidex") == 25.85

    # Verify forecasts structure
    assert len(forecasts) == 9
    first_forecast = forecasts[0]
    assert first_forecast.get("saintName") == "Sylvère"
    assert first_forecast.get("iso") == 4100
    assert first_forecast.get("min") == 22
    assert first_forecast.get("max") == 37
    assert first_forecast.get("rainProbability") == 0

    # Verify rain structure
    assert len(rain) == 9
    assert rain[0].get("desc") == "Temps sec"
    assert rain[0].get("rain") == 1


def test_parse_demain_rsc():
    """Test parsing the demain_rsc_decoded.txt stream (tomorrow page)."""
    content = read_scratch_file("demain_rsc_decoded.txt")
    data = parse_rsc_stream(content)

    assert "realtime" in data
    assert "forecasts" in data
    assert "rain" in data

    # Realtime is still available on layover/headers
    assert data["realtime"].get("temperature") == 22.3

    # Tomorrow page has forecasts list but no rain-in-the-hour
    assert len(data["forecasts"]) > 0
    assert len(data["rain"]) == 0


def test_parse_eightdays_rsc():
    """Test parsing the eightdays_rsc_decoded.txt stream (8-day automatic forecast)."""
    content = read_scratch_file("eightdays_rsc_decoded.txt")
    data = parse_rsc_stream(content)

    assert "realtime" in data
    assert "forecasts" in data
    assert "rain" in data

    # Realtime is still available on layover/headers
    assert data["realtime"].get("temperature") == 22.3

    # Automatic forecast page does not have the expert forecasts list or rain-in-the-hour
    assert len(data["forecasts"]) == 0
    assert len(data["rain"]) == 0


def test_get_today_forecast():
    """Test the get_today_forecast helper function."""
    # 1. Test empty
    assert get_today_forecast([]) is None

    # 2. Test matching today
    today_iso = dt_util.now().strftime("%Y-%m-%d") + "T00:00:00+00:00"

    forecasts = [
        {"day": "2026-06-20T00:00:00+00:00", "saintName": "Sylvère"},
        {"day": today_iso, "saintName": "Aujourd'hui"},
        {"day": "2026-06-22T00:00:00+00:00", "saintName": "Demain"},
    ]

    today_forecast = get_today_forecast(forecasts)
    assert today_forecast is not None
    assert today_forecast.get("saintName") == "Aujourd'hui"

    day1 = (dt_util.now() - timedelta(days=2)).strftime("%Y-%m-%d") + "T00:00:00+00:00"
    day2 = (dt_util.now() - timedelta(days=3)).strftime("%Y-%m-%d") + "T00:00:00+00:00"
    forecasts_no_today = [
        {"day": day1, "saintName": "Sylvère"},
        {"day": day2, "saintName": "Demain"},
    ]
    fallback_forecast = get_today_forecast(forecasts_no_today)
    assert fallback_forecast.get("saintName") == "Sylvère"


def test_get_yesterday_forecast():
    """Test the get_yesterday_forecast helper function."""
    assert get_yesterday_forecast([]) is None

    yesterday_iso = (dt_util.now() - timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00+00:00"

    forecasts = [
        {"day": yesterday_iso, "saintName": "Hier"},
        {"day": "2026-06-22T00:00:00+00:00", "saintName": "Demain"},
    ]

    yesterday_forecast = get_yesterday_forecast(forecasts)
    assert yesterday_forecast is not None
    assert yesterday_forecast.get("saintName") == "Hier"


def test_get_flash_alert():
    """Test the get_flash_alert helper function."""
    assert get_flash_alert([]) is None

    forecasts = [
        {"day": "2026-06-20T00:00:00+00:00", "flash": "$8:2:props:node"},
        {"day": "2026-06-21T00:00:00+00:00", "flash": {"flashLevel": 3, "flashTextHtml": "Warning"}},
    ]

    flash_alert = get_flash_alert(forecasts)
    assert flash_alert is not None
    assert flash_alert.get("flashLevel") == 3
    assert flash_alert.get("flashTextHtml") == "Warning"


def test_pictograms_mapping():
    """Test that pictogram IDs map correctly to conditions and descriptions."""
    # Test standard mappings
    assert map_picto_to_condition(1) == "sunny"
    assert map_picto_to_condition(4) == "cloudy"
    assert map_picto_to_condition(21) == "fog"
    assert map_picto_to_condition(23) == "clear-night"
    assert map_picto_to_condition(44) == "partlycloudy"

    # Test descriptions
    assert map_picto_to_description(1) == "Ciel clair - quasiment pas de nuages et un soleil omniprésent"
    assert map_picto_to_description(4) == "Ciel très nuageux - les nuages l'emportent sur les éclaircies - pas ou très peu de pluie"
    assert map_picto_to_description(21) == "Nuages bas ou brouillard - visibilité généralement réduite à moins de 1 km et rendant la circulation dangereuse"

    # Test fallback/invalid values
    assert map_picto_to_condition(None) is None
    assert map_picto_to_condition(999) is None
    assert map_picto_to_description(None) is None
    assert map_picto_to_description(999) is None
