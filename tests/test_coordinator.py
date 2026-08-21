"""Tests for the Firefly III data update coordinator."""

from unittest.mock import AsyncMock
from types import SimpleNamespace

from pyfirefly import (
    FireflyAuthenticationError,
    FireflyConnectionError,
    FireflyError,
    FireflyTimeoutError,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.firefly_iii.const import DOMAIN
from custom_components.firefly_iii.coordinator import FireflyDataUpdateCoordinator
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

ENTRY_DATA = {
    CONF_URL: "https://firefly.example.com",
    CONF_VERIFY_SSL: True,
    CONF_API_KEY: "test-token",
}


def _make_account(account_id: str, account_type: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=account_id, attributes=SimpleNamespace(type=account_type, name=account_id)
    )


async def _build_coordinator(hass: HomeAssistant) -> FireflyDataUpdateCoordinator:
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA)
    entry.add_to_hass(hass)
    coordinator = FireflyDataUpdateCoordinator(hass, entry)
    coordinator.firefly = AsyncMock()
    return coordinator


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        (FireflyAuthenticationError(), ConfigEntryAuthFailed),
        (FireflyConnectionError(), UpdateFailed),
        (FireflyTimeoutError(), UpdateFailed),
        (FireflyError(), UpdateFailed),
    ],
)
async def test_async_setup_errors(
    hass: HomeAssistant, exception: Exception, expected: type[Exception]
) -> None:
    """Errors from get_about() are translated into the expected exception type."""
    coordinator = await _build_coordinator(hass)
    coordinator.firefly.get_about.side_effect = exception

    with pytest.raises(expected):
        await coordinator._async_setup()


async def test_async_setup_success(hass: HomeAssistant) -> None:
    """A successful get_about() call does not raise."""
    coordinator = await _build_coordinator(hass)
    coordinator.firefly.get_about.return_value = SimpleNamespace()

    await coordinator._async_setup()


async def test_async_update_data_maps_assets_only(hass: HomeAssistant) -> None:
    """Only asset-type accounts are kept in the coordinator data."""
    coordinator = await _build_coordinator(hass)
    asset_account = _make_account("1", "asset")
    expense_account = _make_account("2", "expense")

    coordinator.firefly.get_accounts.return_value = [asset_account, expense_account]
    coordinator.firefly.get_categories.return_value = []
    coordinator.firefly.get_currency_primary.return_value = SimpleNamespace(
        attributes=SimpleNamespace(code="EUR")
    )
    coordinator.firefly.get_budgets.return_value = []
    coordinator.firefly.get_bills.return_value = []

    data = await coordinator._async_update_data()

    assert list(data.accounts) == ["1"]
    assert data.primary_currency.attributes.code == "EUR"


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        (FireflyAuthenticationError(), ConfigEntryAuthFailed),
        (FireflyConnectionError(), UpdateFailed),
        (FireflyTimeoutError(), UpdateFailed),
        (FireflyError(), UpdateFailed),
    ],
)
async def test_async_update_data_errors(
    hass: HomeAssistant, exception: Exception, expected: type[Exception]
) -> None:
    """Errors while fetching data are translated into the expected exception type."""
    coordinator = await _build_coordinator(hass)
    coordinator.firefly.get_accounts.side_effect = exception

    with pytest.raises(expected):
        await coordinator._async_update_data()
