"""Tests for the Météo-Grenoble.com integration lifecycle."""
from unittest.mock import MagicMock, patch
import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.meteo_grenoble.const import DOMAIN
from custom_components.meteo_grenoble.coordinator import MeteoGrenobleDataUpdateCoordinator

from .test_parser import read_scratch_file


async def test_setup_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful setup and unload of the config entry."""
    mock_config_entry.add_to_hass(hass)

    mock_rsc_content = read_scratch_file("home_rsc.txt")

    # Mock the HTTP client response to return the home_rsc.txt stream
    mock_response = MagicMock()
    mock_response.text.return_value = mock_rsc_content

    with patch(
        "homeassistant.helpers.aiohttp_client.async_get_clientsession"
    ) as mock_session_getter:
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session_getter.return_value = mock_session

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


async def test_coordinator_fetch_failure(hass: HomeAssistant, mock_config_entry) -> None:
    """Test coordinator handles network/parsing errors gracefully."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.helpers.aiohttp_client.async_get_clientsession"
    ) as mock_session_getter:
        mock_session = MagicMock()
        # Raise an exception when getting the URL
        mock_session.get.side_effect = Exception("Connection Timeout")
        mock_session_getter.return_value = mock_session

        # Setup integration (will fail first refresh but continue setup if handled)
        # In Home Assistant, if first refresh fails, setup returns True but entry is in setup retry
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
