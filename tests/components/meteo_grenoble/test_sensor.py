"""Tests for the sensor platform of Météo-Grenoble.com."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.meteo_grenoble.const import URL_METEO_GRENOBLE
from tests.components.meteo_grenoble.test_parser import read_scratch_file


async def test_sensor_entities(hass: HomeAssistant, mock_config_entry, aioclient_mock: AiohttpClientMocker, freezer) -> None:
    """Test the sensor entities."""
    freezer.move_to("2026-06-20T15:00:00+00:00")
    mock_config_entry.add_to_hass(hass)

    mock_rsc_content = read_scratch_file("home_rsc.txt")
    aioclient_mock.get(URL_METEO_GRENOBLE, text=mock_rsc_content)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    # Test Temperature
    state = hass.states.get("sensor.meteo_grenoble_com_temperature")
    assert state is not None
    assert float(state.state) == 22.3

    # Test Humidex
    state = hass.states.get("sensor.meteo_grenoble_com_humidex")
    assert state is not None
    assert float(state.state) == 25.85
    assert state.attributes.get("sensation") is not None

    # Test Flash Alert
    state = hass.states.get("sensor.meteo_grenoble_com_alerte_flash")
    assert state is not None
    assert state.state == "Vigilance Orange"
