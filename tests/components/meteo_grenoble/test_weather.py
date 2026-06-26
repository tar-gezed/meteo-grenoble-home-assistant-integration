"""Tests for the weather entity of Météo-Grenoble.com."""
from homeassistant.components.weather import (
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_WIND_SPEED,
    ATTR_WEATHER_PRESSURE,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.meteo_grenoble.const import URL_METEO_GRENOBLE
from tests.components.meteo_grenoble.test_parser import read_scratch_file


async def test_weather_entity(hass: HomeAssistant, mock_config_entry, aioclient_mock: AiohttpClientMocker, freezer) -> None:
    """Test the weather entity states and attributes."""
    freezer.move_to("2026-06-20T15:00:00+00:00")
    mock_config_entry.add_to_hass(hass)

    mock_rsc_content = read_scratch_file("home_rsc.txt")
    aioclient_mock.get(URL_METEO_GRENOBLE, text=mock_rsc_content)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    state = hass.states.get("weather.meteo_grenoble_com")
    assert state is not None
    assert state.state == "sunny"
    
    assert float(state.attributes[ATTR_WEATHER_TEMPERATURE]) == 22.3
    assert float(state.attributes[ATTR_WEATHER_WIND_SPEED]) == 2.88
    assert state.attributes.get(ATTR_WEATHER_PRESSURE) is None
    assert state.attributes.get(ATTR_WEATHER_HUMIDITY) is None
    assert state.attributes.get("wind_bearing") == 225
