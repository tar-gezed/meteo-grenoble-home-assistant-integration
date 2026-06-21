"""Fixtures for Météo-Grenoble.com integration tests."""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteo_grenoble.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Météo-Grenoble.com",
        data={},
        unique_id="meteo_grenoble_test",
    )
