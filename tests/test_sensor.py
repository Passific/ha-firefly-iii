"""Tests for the Firefly III sensor platform."""

from unittest.mock import AsyncMock

from pyfirefly import FireflyConnectionError
from pyfirefly.models import Account
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.firefly_iii.coordinator import DEFAULT_SCAN_INTERVAL
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from . import setup_integration


def _find_entity_id(
    entity_registry: er.EntityRegistry, entry_id: str, unique_id_suffix: str
) -> str:
    """Find the entity_id for this config entry whose unique_id ends with the suffix."""
    for entity in er.async_entries_for_config_entry(entity_registry, entry_id):
        if entity.unique_id.endswith(unique_id_suffix):
            return entity.entity_id
    raise AssertionError(f"No entity found with unique_id suffix {unique_id_suffix!r}")


async def test_all_entities_created(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test that entities are created for each account/category/budget/bill."""
    await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.LOADED

    entities = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    # 1 asset account + 1 category + 1 budget (x3 sensors) + 1 bill (x3 sensors) + 2 aggregates
    assert len(entities) == 1 + 1 + 3 + 3 + 2

    account_balance_id = _find_entity_id(
        entity_registry, mock_config_entry.entry_id, "_account_balance"
    )
    state = hass.states.get(account_balance_id)
    assert state is not None
    assert state.state == "123.45"


async def test_refresh_exceptions(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    freezer,
) -> None:
    """Test entities go unavailable after coordinator refresh failures."""
    await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.LOADED

    account_balance_id = _find_entity_id(
        entity_registry, mock_config_entry.entry_id, "_account_balance"
    )

    mock_firefly_client.get_accounts.side_effect = FireflyConnectionError("down")

    freezer.tick(DEFAULT_SCAN_INTERVAL)
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done(wait_background_tasks=True)

    state = hass.states.get(account_balance_id)
    assert state is not None
    assert state.state == STATE_UNAVAILABLE


async def test_dynamic_new_account_added(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    freezer,
) -> None:
    """Test a newly-created asset account gets a sensor without reloading."""
    await setup_integration(hass, mock_config_entry)

    existing_accounts = mock_firefly_client.get_accounts.return_value
    new_account = Account.from_dict(
        {
            "type": "accounts",
            "id": "99",
            "attributes": {
                "name": "New Vault",
                "type": "asset",
                "current_balance": "42.00",
            },
        }
    )
    mock_firefly_client.get_accounts.return_value = [*existing_accounts, new_account]

    freezer.tick(DEFAULT_SCAN_INTERVAL)
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done(wait_background_tasks=True)

    new_account_entity_id = _find_entity_id(
        entity_registry, mock_config_entry.entry_id, "_account_99_account_balance"
    )
    state = hass.states.get(new_account_entity_id)
    assert state is not None
    assert state.state == "42.0"
