"""Sensor platform for Météo-Grenoble.com."""
from __future__ import annotations

import html
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .__init__ import MeteoGrenobleConfigEntry
from .const import DOMAIN
from .entity import MeteoGrenobleEntity
from .parser import get_today_forecast, get_yesterday_forecast, get_flash_alert
from .picto import map_picto_to_condition, map_picto_to_description

DONATION_PATTERN = re.compile(
    r"IMPORTANT\s*>+\s*Merci pour vos dons,\s*véritables moteurs de ce service gratuit\s*>+\s*Votre soutien nous aide à couvrir les coûts de fonctionnement,\s*à développer de nouvelles fonctionnalités et à garantir un accès libre à l'information pour tous\.?",
    flags=re.IGNORECASE
)
HTML_PATTERN = re.compile(r"<[^>]+>")


@dataclass(frozen=True, kw_only=True)
class MeteoGrenobleSensorEntityDescription(SensorEntityDescription):
    """Class describing Météo-Grenoble.com sensor entities."""

    value_fn: Callable[[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]], Any]
    extra_attrs_fn: Callable[[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]], dict[str, Any] | None] | None = None


def get_humidex_interpretation(val: Any) -> str | None:
    """Interpret humidex value."""
    if val is None:
        return None
    try:
        h_val = float(val)
        if h_val < 30:
            return "Sensation de bien-être"
        if h_val < 35:
            return "Petit inconfort"
        if h_val < 40:
            return "Certain inconfort"
        if h_val < 45:
            return "Beaucoup d'inconfort (évitez les efforts)"
        if h_val <= 54:
            return "Danger (coup de chaleur probable)"
        return "Danger extrême (coup de chaleur imminent)"
    except (ValueError, TypeError):
        return None


def get_realtime_float(key: str) -> Callable:
    def _fn(realtime, forecasts, rain):
        val = realtime.get(key)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
        return None
    return _fn


def get_realtime_str(key: str) -> Callable:
    def _fn(realtime, forecasts, rain):
        return realtime.get(key)
    return _fn


def get_forecast_step_temp(step_idx: int) -> Callable:
    def _fn(realtime, forecasts, rain):
        today = get_today_forecast(forecasts)
        if today:
            steps = today.get("steps", [])
            if len(steps) > step_idx:
                temp = steps[step_idx].get("temp")
                if temp is not None:
                    try:
                        return float(temp)
                    except (ValueError, TypeError):
                        pass
        return None
    return _fn


def get_forecast_step_attrs(step_idx: int) -> Callable:
    def _fn(realtime, forecasts, rain):
        today = get_today_forecast(forecasts)
        yesterday = get_yesterday_forecast(forecasts)
        attrs = {}
        if today:
            today_steps = today.get("steps", [])
            if len(today_steps) > step_idx:
                step_data = today_steps[step_idx]
                picto = step_data.get("picto")
                if picto is not None:
                    attrs["picto_code"] = picto
                    attrs["condition"] = map_picto_to_condition(picto)
                    attrs["picto_description"] = map_picto_to_description(picto)
        if yesterday:
            yesterday_steps = yesterday.get("steps", [])
            if len(yesterday_steps) > step_idx:
                y_step_data = yesterday_steps[step_idx]
                y_temp = y_step_data.get("temp")
                if y_temp is not None:
                    try:
                        attrs["veille_temp"] = float(y_temp)
                    except (ValueError, TypeError):
                        pass
        return attrs if attrs else None
    return _fn


SENSOR_TYPES: tuple[MeteoGrenobleSensorEntityDescription, ...] = (
    MeteoGrenobleSensorEntityDescription(
        key="temperature",
        name="Température",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_realtime_float("temperature"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="humidex",
        name="Humidex",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_realtime_float("humidex"),
        extra_attrs_fn=lambda r, f, rn: {"sensation": get_humidex_interpretation(r.get("humidex"))} if r.get("humidex") is not None else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="humidex_interpretation",
        name="Humidex - Sensation",
        value_fn=lambda r, f, rn: get_humidex_interpretation(r.get("humidex")),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="windchill",
        name="Ressenti au vent",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_realtime_float("windchill"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="humidity",
        name="Humidité",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_realtime_float("humidity"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="wind_speed",
        name="Vitesse du vent",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_realtime_float("wind_speed"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="wind_direction_label",
        name="Direction du vent",
        value_fn=get_realtime_str("wind_direction_label"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="gust",
        name="Rafales",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=get_realtime_float("gust"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="max_wind_speed_since_00h",
        name="Vent max depuis 00h",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=get_realtime_float("max_wind_speed_since_00h"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="pressure",
        name="Pression",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=get_realtime_float("pressure"),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="rain_hour",
        name="Pluie dans l'heure",
        value_fn=lambda r, f, rn: rn[0].get("desc", "Temps sec") if rn else "Donnée indisponible",
        extra_attrs_fn=lambda r, f, rn: {"forecast": [{"time": item.get("dt"), "rain": item.get("rain"), "desc": item.get("desc")} for item in rn]} if rn else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="saintName",
        name="Saint du jour",
        value_fn=lambda r, f, rn: get_today_forecast(f).get("saintName") if get_today_forecast(f) else None,
        extra_attrs_fn=lambda r, f, rn: {"gender": get_today_forecast(f).get("saintGender")} if get_today_forecast(f) else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="iso",
        name="Isotherme 0°C",
        native_unit_of_measurement="m",
        value_fn=lambda r, f, rn: int(get_today_forecast(f).get("iso")) if get_today_forecast(f) and get_today_forecast(f).get("iso") is not None else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="fiability",
        name="Fiabilité",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda r, f, rn: int(get_today_forecast(f).get("fiability")) if get_today_forecast(f) and get_today_forecast(f).get("fiability") is not None else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="flash",
        name="Alerte Flash",
        value_fn=lambda r, f, rn: (
            {
                0: "Pas d'alerte",
                1: "Vigilance Jaune",
                2: "Vigilance Orange",
                3: "Vigilance Orange",
                4: "Vigilance Rouge",
            }.get(get_flash_alert(f).get("flashLevel", 0), f"Niveau {get_flash_alert(f).get('flashLevel', 0)}")
            if isinstance(get_flash_alert(f), dict) else "Pas d'alerte"
        ),
        extra_attrs_fn=lambda r, f, rn: (
            lambda flash: {
                "text": DONATION_PATTERN.sub(
                    " ",
                    html.unescape(HTML_PATTERN.sub("", flash.get("flashTextHtml", ""))).strip(),
                ).strip(),
                "updated_at": flash.get("flashUpdatedAt"),
                "level": flash.get("flashLevel"),
            } if isinstance(flash, dict) else None
        )(get_flash_alert(f)),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="tempGap",
        name="Écart de température de saison",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda r, f, rn: float(get_today_forecast(f).get("tempGap")) if get_today_forecast(f) and get_today_forecast(f).get("tempGap") is not None else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="dayLegend",
        name="Description météo du jour",
        value_fn=lambda r, f, rn: get_today_forecast(f).get("dayLegend") if get_today_forecast(f) else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="updated_at",
        name="Dernière mise à jour",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda r, f, rn: dt_util.parse_datetime(r.get("updated_at")) if r.get("updated_at") else None,
    ),
    MeteoGrenobleSensorEntityDescription(
        key="forecast_today_matin",
        name="Météo Matin",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_forecast_step_temp(0),
        extra_attrs_fn=get_forecast_step_attrs(0),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="forecast_today_afternoon",
        name="Météo Après-midi",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_forecast_step_temp(1),
        extra_attrs_fn=get_forecast_step_attrs(1),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="forecast_today_evening",
        name="Météo Soir",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_forecast_step_temp(2),
        extra_attrs_fn=get_forecast_step_attrs(2),
    ),
    MeteoGrenobleSensorEntityDescription(
        key="forecast_today_night",
        name="Météo Nuit",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=get_forecast_step_temp(3),
        extra_attrs_fn=get_forecast_step_attrs(3),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoGrenobleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Météo-Grenoble.com sensor platform."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            MeteoGrenobleSensor(coordinator, entry, description)
            for description in SENSOR_TYPES
        ],
        True,
    )


class MeteoGrenobleSensor(MeteoGrenobleEntity, SensorEntity):
    """Representation of a Météo-Grenoble.com sensor."""

    entity_description: MeteoGrenobleSensorEntityDescription

    def __init__(
        self, coordinator, entry: MeteoGrenobleConfigEntry, description: MeteoGrenobleSensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        realtime = self.coordinator.data.get("realtime", {})
        forecasts = self.coordinator.data.get("forecasts", [])
        rain = self.coordinator.data.get("rain", [])

        return self.entity_description.value_fn(realtime, forecasts, rain)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the extra state attributes."""
        if not self.entity_description.extra_attrs_fn:
            return None

        realtime = self.coordinator.data.get("realtime", {})
        forecasts = self.coordinator.data.get("forecasts", [])
        rain = self.coordinator.data.get("rain", [])

        return self.entity_description.extra_attrs_fn(realtime, forecasts, rain)
