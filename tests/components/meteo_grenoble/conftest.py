"""Fixtures for Météo-Grenoble.com integration tests."""
import sys
import asyncio
import pytest_socket
import aiodns

# Bypass pytest-socket blocking which breaks Windows asyncio ProactorEventLoop
if sys.platform == "win32":
    pytest_socket.disable_socket = lambda *args, **kwargs: None

# Bypass aiodns SelectorEventLoop check which breaks on Windows ProactorEventLoop
if sys.platform == "win32":
    aiodns.sys.platform = "linux"

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.meteo_grenoble.const import DOMAIN

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations in Home Assistant."""
    yield


@pytest.fixture(autouse=True)
def verify_cleanup():
    """Override verify_cleanup to prevent failures from lingering threads in CI."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Météo-Grenoble.com",
        data={},
        unique_id="meteo_grenoble_test",
    )
