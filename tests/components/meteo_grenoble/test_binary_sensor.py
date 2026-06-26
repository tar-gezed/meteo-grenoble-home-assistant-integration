"""Tests for the binary sensor platform of Météo-Grenoble.com."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.meteo_grenoble.const import URL_METEO_GRENOBLE
from tests.components.meteo_grenoble.test_parser import read_scratch_file


async def test_binary_sensor_entities(hass: HomeAssistant, mock_config_entry, aioclient_mock: AiohttpClientMocker, freezer) -> None:
    """Test the binary sensor entities."""
    freezer.move_to("2026-06-20T15:00:00+00:00")
    mock_config_entry.add_to_hass(hass)

    mock_rsc_content = read_scratch_file("home_rsc.txt")
    aioclient_mock.get(URL_METEO_GRENOBLE, text=mock_rsc_content)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    state = hass.states.get("binary_sensor.meteo_grenoble_com_vigilance_canicule")
    assert state is not None
    assert state.state in ("on", "off")

    state = hass.states.get("binary_sensor.meteo_grenoble_com_vigilance_neige")
    assert state is not None
    assert state.state in ("on", "off")
