"""Sensor platform for Météo-Grenoble.com."""
from __future__ import annotations

from typing import Any, Dict, List

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN
from .parser import get_today_forecast, get_yesterday_forecast, get_flash_alert
from .picto import map_picto_to_condition, map_picto_to_description

# Description of all sensors
SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        name="Température",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidex",
        name="Humidex",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidex_interpretation",
        name="Humidex - Sensation",
    ),
    SensorEntityDescription(
        key="windchill",
        name="Ressenti au vent",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidity",
        name="Humidité",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="wind_speed",
        name="Vitesse du vent",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wind_direction_label",
        name="Direction du vent",
    ),
    SensorEntityDescription(
        key="gust",
        name="Rafales",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="max_wind_speed_since_00h",
        name="Vent max depuis 00h",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="pressure",
        name="Pression",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="rain_hour",
        name="Pluie dans l'heure",
    ),
    SensorEntityDescription(
        key="saintName",
        name="Saint du jour",
    ),
    SensorEntityDescription(
        key="iso",
        name="Isotherme 0°C",
        native_unit_of_measurement="m",
    ),
    SensorEntityDescription(
        key="fiability",
        name="Fiabilité",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="flash",
        name="Alerte Flash",
    ),
    SensorEntityDescription(
        key="tempGap",
        name="Écart de température de saison",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dayLegend",
        name="Description météo du jour",
    ),
    SensorEntityDescription(
        key="updated_at",
        name="Dernière mise à jour",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key="forecast_today_matin",
        name="Météo Matin",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="forecast_today_afternoon",
        name="Météo Après-midi",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="forecast_today_evening",
        name="Météo Soir",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="forecast_today_night",
        name="Météo Nuit",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Météo-Grenoble.com sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MeteoGrenobleSensor(coordinator, entry, description)
            for description in SENSOR_TYPES
        ],
        True,
    )


class MeteoGrenobleSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Météo-Grenoble.com sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator, entry: ConfigEntry, description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer="Météo Grenoble",
            model="meteo-grenoble.com",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        key = self.entity_description.key
        realtime = self.coordinator.data.get("realtime", {})
        forecasts = self.coordinator.data.get("forecasts", [])
        rain = self.coordinator.data.get("rain", [])

        # 1. Realtime station sensors
        if key in [
            "temperature",
            "humidex",
            "windchill",
            "humidity",
            "wind_speed",
            "wind_direction_label",
            "gust",
            "max_wind_speed_since_00h",
            "pressure",
        ]:
            val = realtime.get(key)
            if val is not None:
                # Ensure correct types
                if key in ["temperature", "humidex", "windchill", "humidity", "wind_speed", "gust", "max_wind_speed_since_00h", "pressure"]:
                    return float(val)
                return val
            return None

        # 1.5 Last update sensor
        if key == "updated_at":
            val = realtime.get("updated_at")
            if val:
                from datetime import datetime
                try:
                    return datetime.fromisoformat(val.replace("Z", "+00:00"))
                except ValueError:
                    pass
            return None

        # 2. Rain forecast sensor
        if key == "rain_hour":
            if not rain:
                return "Donnée indisponible"
            return rain[0].get("desc", "Temps sec")

        # 2.5 Humidex interpretation sensor
        if key == "humidex_interpretation":
            val = realtime.get("humidex")
            if val is not None:
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
                except ValueError:
                    pass
            return None

        # 3. Forecast/Saint/Alert/Period sensors
        if forecasts:
            today = get_today_forecast(forecasts)
            if today:
                if key == "saintName":
                    return today.get("saintName")
                if key == "iso":
                    val = today.get("iso")
                    return int(val) if val is not None else None
                if key == "fiability":
                    val = today.get("fiability")
                    return int(val) if val is not None else None
                if key == "flash":
                    flash_data = get_flash_alert(forecasts)
                    if isinstance(flash_data, dict):
                        level = flash_data.get("flashLevel", 0)
                        return {
                            0: "Pas d'alerte",
                            1: "Vigilance Jaune",
                            2: "Vigilance Orange",
                            3: "Vigilance Orange",
                            4: "Vigilance Rouge",
                        }.get(level, f"Niveau {level}")
                    return "Pas d'alerte"
                if key == "tempGap":
                    val = today.get("tempGap")
                    return float(val) if val is not None else None
                if key == "dayLegend":
                    return today.get("dayLegend")
                if key in [
                    "forecast_today_matin",
                    "forecast_today_afternoon",
                    "forecast_today_evening",
                    "forecast_today_night",
                ]:
                    step_idx = {
                        "forecast_today_matin": 0,
                        "forecast_today_afternoon": 1,
                        "forecast_today_evening": 2,
                        "forecast_today_night": 3,
                    }[key]
                    steps = today.get("steps", [])
                    if len(steps) > step_idx:
                        temp = steps[step_idx].get("temp")
                        return float(temp) if temp is not None else None

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the extra state attributes."""
        key = self.entity_description.key

        # Extra attributes for humidex sensor
        if key == "humidex":
            realtime = self.coordinator.data.get("realtime", {})
            val = realtime.get("humidex")
            if val is not None:
                try:
                    h_val = float(val)
                    if h_val < 30:
                        sensation = "Sensation de bien-être"
                    elif h_val < 35:
                        sensation = "Petit inconfort"
                    elif h_val < 40:
                        sensation = "Certain inconfort"
                    elif h_val < 45:
                        sensation = "Beaucoup d'inconfort (évitez les efforts)"
                    elif h_val <= 54:
                        sensation = "Danger (coup de chaleur probable)"
                    else:
                        sensation = "Danger extrême (coup de chaleur imminent)"
                    return {"sensation": sensation}
                except ValueError:
                    pass

        # Extra attributes for rain in the hour sensor
        if key == "rain_hour":
            rain = self.coordinator.data.get("rain", [])
            if rain:
                return {
                    "forecast": [
                        {
                            "time": item.get("dt"),
                            "rain": item.get("rain"),
                            "desc": item.get("desc"),
                        }
                        for item in rain
                    ]
                }

        # Extra attributes for flash alert sensor
        if key == "flash":
            forecasts = self.coordinator.data.get("forecasts", [])
            flash_data = get_flash_alert(forecasts)
            if isinstance(flash_data, dict):
                import html
                import re
                raw_text = flash_data.get("flashTextHtml", "")
                clean_text = re.sub(r"<[^>]+>", "", raw_text)
                clean_text = html.unescape(clean_text).strip()
                
                # Remove recurring donation/support advertisement message
                donation_pattern = (
                    r"\s*IMPORTANT\s*>+\s*Merci pour vos dons,\s*véritables moteurs de "
                    r"ce service gratuit\s*>+\s*Votre soutien nous aide à couvrir les "
                    r"coûts de fonctionnement,\s*à développer de nouvelles fonctionnalités "
                    r"et à garantir un accès libre à l'information pour tous\.?\s*"
                )
                clean_text = re.sub(donation_pattern, " ", clean_text, flags=re.IGNORECASE).strip()
                
                return {
                    "text": clean_text,
                    "updated_at": flash_data.get("flashUpdatedAt"),
                    "level": flash_data.get("flashLevel"),
                }

        # Extra attributes for saint sensor
        if key == "saintName":
            forecasts = self.coordinator.data.get("forecasts", [])
            if forecasts:
                today = get_today_forecast(forecasts)
                if today:
                    return {
                        "gender": today.get("saintGender"),
                    }

        # Extra attributes for detailed forecast steps (Matin, Après-midi, Soir, Nuit)
        if key in [
            "forecast_today_matin",
            "forecast_today_afternoon",
            "forecast_today_evening",
            "forecast_today_night",
        ]:
            step_idx = {
                "forecast_today_matin": 0,
                "forecast_today_afternoon": 1,
                "forecast_today_evening": 2,
                "forecast_today_night": 3,
            }[key]
            forecasts = self.coordinator.data.get("forecasts", [])
            if forecasts:
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
                            attrs["veille_temp"] = float(y_temp)
                            
                return attrs if attrs else None

        return None
