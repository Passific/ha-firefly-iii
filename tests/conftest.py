"""Fixtures for Firefly III integration tests."""

from collections.abc import Generator
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

from pyfirefly.models import (
    About,
    Account,
    Bill,
    Budget,
    BudgetLimitAttributes,
    Category,
    Currency,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.firefly_iii.const import DOMAIN
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL

pytest_plugins = "pytest_homeassistant_custom_component"

FIXTURES_DIR = Path(__file__).parent / "fixtures"

MOCK_TEST_CONFIG = {
    CONF_URL: "https://127.0.0.1:8080/",
    CONF_API_KEY: "test_api_key",
    CONF_VERIFY_SSL: True,
}


def _load_fixture(filename: str):
    """Load a JSON fixture from the tests/fixtures directory."""
    return json.loads((FIXTURES_DIR / filename).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for every test."""
    yield


@pytest.fixture(name="mock_setup_entry")
def mock_setup_entry_fixture() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.firefly_iii.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(name="mock_firefly_client")
def mock_firefly_client_fixture() -> Generator[AsyncMock]:
    """Mock the pyfirefly client with data from tests/fixtures."""
    with (
        patch("custom_components.firefly_iii.config_flow.Firefly") as mock_client,
        patch(
            "custom_components.firefly_iii.coordinator.Firefly", new=mock_client
        ),
    ):
        client = mock_client.return_value

        client.get_about = AsyncMock(
            return_value=About.from_dict(_load_fixture("about.json"))
        )
        client.get_accounts = AsyncMock(
            return_value=[
                Account.from_dict(account)
                for account in _load_fixture("accounts.json")
            ]
        )
        client.get_categories = AsyncMock(
            return_value=[
                Category.from_dict(category)
                for category in _load_fixture("categories.json")
            ]
        )
        client.get_category = AsyncMock(
            return_value=Category.from_dict(_load_fixture("category.json"))
        )
        client.get_currency_primary = AsyncMock(
            return_value=Currency.from_dict(_load_fixture("primary_currency.json"))
        )
        client.get_budgets = AsyncMock(
            return_value=[
                Budget.from_dict(budget) for budget in _load_fixture("budgets.json")
            ]
        )
        client.get_budget_limits = AsyncMock(
            return_value=[
                BudgetLimitAttributes.from_dict(limit)
                for limit in _load_fixture("budget_limits.json")
            ]
        )
        client.get_bills = AsyncMock(
            return_value=[
                Bill.from_dict(bill) for bill in _load_fixture("bills.json")
            ]
        )
        yield client


@pytest.fixture(name="mock_config_entry")
def mock_config_entry_fixture() -> MockConfigEntry:
    """Mock a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Firefly III test",
        data=MOCK_TEST_CONFIG,
        entry_id="firefly_iii_test_entry_123",
        unique_id=None,
    )
