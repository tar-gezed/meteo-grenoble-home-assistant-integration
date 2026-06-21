"""Tests for the Météo-Grenoble.com integration lifecycle."""
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.meteo_grenoble.const import DOMAIN, URL_METEO_GRENOBLE
from custom_components.meteo_grenoble.coordinator import MeteoGrenobleDataUpdateCoordinator

from tests.components.meteo_grenoble.test_parser import read_scratch_file
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker


async def test_setup_unload_entry(hass: HomeAssistant, mock_config_entry, aioclient_mock: AiohttpClientMocker, freezer) -> None:
    """Test successful setup and unload of the config entry."""
    freezer.move_to("2026-06-20T15:00:00+00:00")
    mock_config_entry.add_to_hass(hass)

    mock_rsc_content = read_scratch_file("home_rsc.txt")

    # Mock the HTTP client response to return the home_rsc.txt stream
    aioclient_mock.get(URL_METEO_GRENOBLE, text=mock_rsc_content)

    # Setup integration
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Check entry state
    assert mock_config_entry.state is ConfigEntryState.LOADED

    # Verify coordinator data exists
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
    assert isinstance(coordinator, MeteoGrenobleDataUpdateCoordinator)
    assert coordinator.data["realtime"]["temperature"] == 22.3

    # Verify some entities were created
    # Main weather entity
    weather_state = hass.states.get("weather.meteo_grenoble_com")
    assert weather_state is not None
    assert weather_state.state == "partlycloudy"
    assert float(weather_state.attributes["temperature"]) == 22.3

    # Individual temperature sensor
    temp_state = hass.states.get("sensor.meteo_grenoble_com_temperature")
    assert temp_state is not None
    assert float(temp_state.state) == 22.3

    # Rain hour sensor
    rain_state = hass.states.get("sensor.meteo_grenoble_com_pluie_dans_l_heure")
    assert rain_state is not None
    assert rain_state.state == "Temps sec"

    # Vigilance Heat binary sensor
    vigilance_heat = hass.states.get("binary_sensor.meteo_grenoble_com_vigilance_canicule")
    assert vigilance_heat is not None
    assert vigilance_heat.state == "on"

    # Unload integration
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


async def test_coordinator_fetch_failure(hass: HomeAssistant, mock_config_entry, aioclient_mock: AiohttpClientMocker) -> None:
    """Test coordinator handles network/parsing errors gracefully."""
    mock_config_entry.add_to_hass(hass)

    # Mock connection timeout
    aioclient_mock.get(URL_METEO_GRENOBLE, exc=Exception("Connection Timeout"))

    # Setup integration (will fail first refresh but continue setup if handled)
    # In Home Assistant, if first refresh fails, setup returns True but entry is in setup retry
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
