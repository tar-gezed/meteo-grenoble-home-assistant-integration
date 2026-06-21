"""Tests for the Météo-Grenoble.com data parser."""
import os
import unittest

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


class TestMeteoGrenobleParser(unittest.TestCase):
    """Unit tests for the Next.js RSC parser."""

    def test_parse_empty_stream(self):
        """Test that parsing an empty stream raises a ValueError."""
        with self.assertRaisesRegex(ValueError, "Empty response received"):
            parse_rsc_stream("")

        with self.assertRaisesRegex(ValueError, "Empty response received"):
            parse_rsc_stream("   \n   ")

    def test_parse_invalid_stream(self):
        """Test that parsing an invalid stream raises a ValueError."""
        with self.assertRaisesRegex(ValueError, "Could not find weather data"):
            parse_rsc_stream("1:I[1, 2, 3]\n2:T[4, 5, 6]")

    def test_parse_home_rsc(self):
        """Test parsing the home_rsc.txt stream (main homepage)."""
        content = read_scratch_file("home_rsc.txt")
        data = parse_rsc_stream(content)

        self.assertIn("realtime", data)
        self.assertIn("forecasts", data)
        self.assertIn("rain", data)

        realtime = data["realtime"]
        forecasts = data["forecasts"]
        rain = data["rain"]

        # Verify realtime structure
        self.assertIsInstance(realtime.get("temperature"), (int, float))
        self.assertEqual(realtime.get("temperature"), 22.3)
        self.assertEqual(realtime.get("wind_direction_label"), "Sud-Ouest")
        self.assertEqual(realtime.get("humidex"), 25.85)

        # Verify forecasts structure
        self.assertEqual(len(forecasts), 9)
        first_forecast = forecasts[0]
        self.assertEqual(first_forecast.get("saintName"), "Sylvère")
        self.assertEqual(first_forecast.get("iso"), 4100)
        self.assertEqual(first_forecast.get("min"), 22)
        self.assertEqual(first_forecast.get("max"), 37)
        self.assertEqual(first_forecast.get("rainProbability"), 0)

        # Verify rain structure
        self.assertEqual(len(rain), 9)
        self.assertEqual(rain[0].get("desc"), "Temps sec")
        self.assertEqual(rain[0].get("rain"), 1)

    def test_parse_demain_rsc(self):
        """Test parsing the demain_rsc_decoded.txt stream (tomorrow page)."""
        content = read_scratch_file("demain_rsc_decoded.txt")
        data = parse_rsc_stream(content)

        self.assertIn("realtime", data)
        self.assertIn("forecasts", data)
        self.assertIn("rain", data)

        # Realtime is still available on layover/headers
        self.assertEqual(data["realtime"].get("temperature"), 22.3)

        # Tomorrow page has forecasts list but no rain-in-the-hour
        self.assertGreater(len(data["forecasts"]), 0)
        self.assertEqual(len(data["rain"]), 0)

    def test_parse_eightdays_rsc(self):
        """Test parsing the eightdays_rsc_decoded.txt stream (8-day automatic forecast)."""
        content = read_scratch_file("eightdays_rsc_decoded.txt")
        data = parse_rsc_stream(content)

        self.assertIn("realtime", data)
        self.assertIn("forecasts", data)
        self.assertIn("rain", data)

        # Realtime is still available on layover/headers
        self.assertEqual(data["realtime"].get("temperature"), 22.3)

        # Automatic forecast page does not have the expert forecasts list or rain-in-the-hour
        self.assertEqual(len(data["forecasts"]), 0)
        self.assertEqual(len(data["rain"]), 0)

    def test_get_today_forecast(self):
        """Test the get_today_forecast helper function."""
        # 1. Test empty
        self.assertIsNone(get_today_forecast([]))

        # 2. Test matching today
        from datetime import datetime
        today_iso = datetime.now().strftime("%Y-%m-%d") + "T00:00:00+00:00"

        forecasts = [
            {"day": "2026-06-20T00:00:00+00:00", "saintName": "Sylvère"},
            {"day": today_iso, "saintName": "Aujourd'hui"},
            {"day": "2026-06-22T00:00:00+00:00", "saintName": "Demain"},
        ]

        today_forecast = get_today_forecast(forecasts)
        self.assertIsNotNone(today_forecast)
        self.assertEqual(today_forecast.get("saintName"), "Aujourd'hui")

        # 3. Test fallback to first if today is not in list
        forecasts_no_today = [
            {"day": "2026-06-20T00:00:00+00:00", "saintName": "Sylvère"},
            {"day": "2026-06-22T00:00:00+00:00", "saintName": "Demain"},
        ]
        fallback_forecast = get_today_forecast(forecasts_no_today)
        self.assertEqual(fallback_forecast.get("saintName"), "Sylvère")

    def test_get_yesterday_forecast(self):
        """Test the get_yesterday_forecast helper function."""
        self.assertIsNone(get_yesterday_forecast([]))

        from datetime import datetime, timedelta
        yesterday_iso = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d") + "T00:00:00+00:00"

        forecasts = [
            {"day": yesterday_iso, "saintName": "Hier"},
            {"day": "2026-06-22T00:00:00+00:00", "saintName": "Demain"},
        ]

        yesterday_forecast = get_yesterday_forecast(forecasts)
        self.assertIsNotNone(yesterday_forecast)
        self.assertEqual(yesterday_forecast.get("saintName"), "Hier")

    def test_get_flash_alert(self):
        """Test the get_flash_alert helper function."""
        self.assertIsNone(get_flash_alert([]))

        forecasts = [
            {"day": "2026-06-20T00:00:00+00:00", "flash": "$8:2:props:node"},
            {"day": "2026-06-21T00:00:00+00:00", "flash": {"flashLevel": 3, "flashTextHtml": "Warning"}},
        ]

        flash_alert = get_flash_alert(forecasts)
        self.assertIsNotNone(flash_alert)
        self.assertEqual(flash_alert.get("flashLevel"), 3)
        self.assertEqual(flash_alert.get("flashTextHtml"), "Warning")

    def test_pictograms_mapping(self):
        """Test that pictogram IDs map correctly to conditions and descriptions."""
        # Test standard mappings
        self.assertEqual(map_picto_to_condition(1), "sunny")
        self.assertEqual(map_picto_to_condition(4), "cloudy")
        self.assertEqual(map_picto_to_condition(21), "fog")
        self.assertEqual(map_picto_to_condition(23), "clear-night")
        self.assertEqual(map_picto_to_condition(44), "partlycloudy")

        # Test descriptions
        self.assertEqual(
            map_picto_to_description(1),
            "Ciel clair - quasiment pas de nuages et un soleil omniprésent"
        )
        self.assertEqual(
            map_picto_to_description(4),
            "Ciel très nuageux - les nuages l'emportent sur les éclaircies - pas ou très peu de pluie"
        )
        self.assertEqual(
            map_picto_to_description(21),
            "Nuages bas ou brouillard - visibilité généralement réduite à moins de 1 km et rendant la circulation dangereuse"
        )

        # Test fallback/invalid values
        self.assertEqual(map_picto_to_condition(None), "cloudy")
        self.assertEqual(map_picto_to_condition(999), "cloudy")
        self.assertIsNone(map_picto_to_description(None))
        self.assertIsNone(map_picto_to_description(999))


if __name__ == "__main__":
    unittest.main()
