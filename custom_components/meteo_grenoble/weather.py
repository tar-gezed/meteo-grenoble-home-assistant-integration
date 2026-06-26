"""Weather platform for Météo-Grenoble.com."""
from __future__ import annotations

from typing import Any

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .__init__ import MeteoGrenobleConfigEntry
from .const import DOMAIN
from .entity import MeteoGrenobleEntity
from .parser import get_today_forecast
from .picto import map_picto_to_condition, map_picto_to_description


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoGrenobleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Météo-Grenoble.com weather platform."""
    coordinator = entry.runtime_data
    async_add_entities([MeteoGrenobleWeather(coordinator, entry)], True)


WIND_DIRECTION_MAP = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSW": 202.5,
    "SW": 225,
    "WSW": 247.5,
    "W": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5,
}


def _safe_float(val: Any) -> float | None:
    """Safely convert value to float, catching ValueError."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


class MeteoGrenobleWeather(MeteoGrenobleEntity, WeatherEntity):
    """Representation of the weather at Grenoble."""

    _attr_name = None
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    def __init__(self, coordinator, entry: MeteoGrenobleConfigEntry) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{DOMAIN}_weather"

    @property
    def _current_picto(self) -> int | None:
        """Return the current picto code."""
        forecasts = self.coordinator.data.get("forecasts", [])
        if not forecasts:
            return None

        today = get_today_forecast(forecasts)
        if not today:
            return None
        steps = today.get("steps", [])
        if not steps:
            return None

        # Determine current condition based on current time
        # Matin (0), Après-midi (1), Soir (2), Nuit (3)
        current_hour = dt_util.now().hour

        if len(steps) == 4:
            if 6 <= current_hour < 12:
                return steps[0].get("picto")
            if 12 <= current_hour < 18:
                return steps[1].get("picto")
            if 18 <= current_hour < 22:
                return steps[2].get("picto")
            return steps[3].get("picto")
        if len(steps) > 0:
            return steps[0].get("picto")

        return None

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        picto = self._current_picto
        return map_picto_to_condition(picto)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the extra state attributes."""
        picto = self._current_picto
        if picto is not None:
            return {
                "picto_code": picto,
                "picto_description": map_picto_to_description(picto),
            }
        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        realtime = self.coordinator.data.get("realtime", {})
        temp = realtime.get("temperature")
        if temp is not None:
            return _safe_float(temp)

        # Fallback to currentTemp or today's min/max average
        forecasts = self.coordinator.data.get("forecasts", [])
        if forecasts:
            today = get_today_forecast(forecasts)
            if today and "currentTemp" in today and today["currentTemp"] is not None:
                return _safe_float(today["currentTemp"])
            if "max" in today and today["max"] is not None:
                return _safe_float(today["max"])

        return None

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        realtime = self.coordinator.data.get("realtime", {})
        humidity = realtime.get("humidity")
        if humidity is not None:
            return _safe_float(humidity)
        return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        realtime = self.coordinator.data.get("realtime", {})
        wind_speed = realtime.get("wind_speed")
        if wind_speed is not None:
            return _safe_float(wind_speed)
        return None

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind direction."""
        realtime = self.coordinator.data.get("realtime", {})
        direction = realtime.get("wind_direction")
        if direction in WIND_DIRECTION_MAP:
            return WIND_DIRECTION_MAP[direction]
        return None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        realtime = self.coordinator.data.get("realtime", {})
        pressure = realtime.get("pressure")
        if pressure is not None:
            return _safe_float(pressure)
        return None

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        forecasts = self.coordinator.data.get("forecasts", [])
        if not forecasts:
            return None

        today_local = dt_util.start_of_local_day().date()
        forecast_list: list[Forecast] = []
        for day in forecasts:
            day_str = day.get("day", "")
            if not day_str:
                continue
            try:
                forecast_date = dt_util.parse_datetime(day_str).date()
                if forecast_date < today_local:
                    continue
            except Exception:
                pass

            steps = day.get("steps", [])
            # For daily condition, pick afternoon picto (index 1) if available,
            # otherwise pick first available step.
            picto = None
            if len(steps) >= 2:
                picto = steps[1].get("picto")
            elif len(steps) > 0:
                picto = steps[0].get("picto")

            forecast_list.append(
                {
                    "datetime": day.get("day", ""),
                    "native_temperature": _safe_float(day.get("max")),
                    "native_templow": _safe_float(day.get("min")),
                    "native_precipitation": _safe_float(day.get("rain24")),
                    "precipitation_probability": int(day.get("rainProbability")) if day.get("rainProbability") is not None else None,
                    "condition": map_picto_to_condition(picto),
                    "description": day.get("dayLegend"),
                    "picto_description": map_picto_to_description(picto),
                    "temp_gap": _safe_float(day.get("tempGap")),
                }
            )

        return forecast_list

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Service call to retrieve the daily forecast."""
        return self._async_forecast_daily()
