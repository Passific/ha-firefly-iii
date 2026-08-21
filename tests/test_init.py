"""Tests for the Firefly III integration setup."""

from unittest.mock import AsyncMock

from pyfirefly import (
    FireflyAuthenticationError,
    FireflyConnectionError,
    FireflyTimeoutError,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from . import setup_integration


@pytest.mark.parametrize(
    ("exception", "expected_state"),
    [
        (FireflyAuthenticationError("bad creds"), ConfigEntryState.SETUP_ERROR),
        (FireflyConnectionError("cannot connect"), ConfigEntryState.SETUP_RETRY),
        (FireflyTimeoutError("timeout"), ConfigEntryState.SETUP_RETRY),
    ],
)
async def test_setup_exceptions(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    exception: Exception,
    expected_state: ConfigEntryState,
) -> None:
    """Test that setup failures put the config entry in the expected state."""
    mock_firefly_client.get_about.side_effect = exception
    await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is expected_state


async def test_setup_and_unload(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup succeeds and the entry can be cleanly unloaded."""
    await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.LOADED

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
