"""Fixtures for Firefly III integration tests."""

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for every test."""
    yield


@pytest.fixture(name="mock_setup_entry")
def mock_setup_entry_fixture(hass):
    """Prevent actual coordinator setup from running during config flow tests."""
    from unittest.mock import patch

    with patch(
        "custom_components.firefly_iii.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup
