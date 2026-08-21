"""Tests for the Firefly III config flow."""

from unittest.mock import AsyncMock, MagicMock

from pyfirefly import (
    FireflyAuthenticationError,
    FireflyConnectionError,
    FireflyTimeoutError,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.firefly_iii.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import MOCK_TEST_CONFIG

USER_INPUT_RECONFIGURE = {
    CONF_URL: "https://new_domain:9000/",
    CONF_API_KEY: "new_api_key",
    CONF_VERIFY_SSL: True,
}


@pytest.mark.usefixtures("mock_setup_entry")
async def test_form_and_flow(
    hass: HomeAssistant, mock_firefly_client: MagicMock
) -> None:
    """Test we get the form and can complete the flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_TEST_CONFIG
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_TEST_CONFIG[CONF_URL]
    assert result["data"] == MOCK_TEST_CONFIG


@pytest.mark.parametrize(
    ("exception", "reason"),
    [
        (FireflyAuthenticationError, "invalid_auth"),
        (FireflyConnectionError, "cannot_connect"),
        (FireflyTimeoutError, "timeout_connect"),
        (Exception("Some other error"), "unknown"),
    ],
)
@pytest.mark.usefixtures("mock_setup_entry")
async def test_form_exceptions(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    exception: Exception,
    reason: str,
) -> None:
    """Test we handle all exceptions and can recover afterwards."""
    mock_firefly_client.get_about.side_effect = exception

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_TEST_CONFIG
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": reason}

    mock_firefly_client.get_about.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_TEST_CONFIG
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == MOCK_TEST_CONFIG


async def test_duplicate_entry(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test we handle duplicate entries by URL."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_TEST_CONFIG
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_full_flow_reauth(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_setup_entry: MagicMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the reauth flow updates the token on the existing entry."""
    mock_config_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_API_KEY: "new_api_key"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_API_KEY] == "new_api_key"
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    ("exception", "reason"),
    [
        (FireflyAuthenticationError, "invalid_auth"),
        (FireflyConnectionError, "cannot_connect"),
        (FireflyTimeoutError, "timeout_connect"),
        (Exception("Some other error"), "unknown"),
    ],
)
async def test_reauth_flow_exceptions(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_setup_entry: MagicMock,
    mock_config_entry: MockConfigEntry,
    exception: Exception,
    reason: str,
) -> None:
    """Test we handle all exceptions in the reauth flow, and can recover."""
    mock_config_entry.add_to_hass(hass)
    mock_firefly_client.get_about.side_effect = exception

    result = await mock_config_entry.start_reauth_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_API_KEY: "new_api_key"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": reason}

    mock_firefly_client.get_about.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_API_KEY: "new_api_key"}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_API_KEY] == "new_api_key"
    assert len(mock_setup_entry.mock_calls) == 1


async def test_full_flow_reconfigure(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_setup_entry: MagicMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the reconfigure flow updates the existing entry."""
    mock_config_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=USER_INPUT_RECONFIGURE
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_API_KEY] == "new_api_key"
    assert mock_config_entry.data[CONF_URL] == "https://new_domain:9000/"
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.usefixtures("mock_setup_entry")
async def test_full_flow_reconfigure_duplicate(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test reconfiguring to a URL that is already used by another entry aborts."""
    mock_config_entry.add_to_hass(hass)
    duplicate_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_URL: "https://duplicate-url/",
            CONF_API_KEY: "other_key",
            CONF_VERIFY_SSL: True,
        },
    )
    duplicate_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_URL: "https://duplicate-url/",
            CONF_API_KEY: "new_key",
            CONF_VERIFY_SSL: True,
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("exception", "reason"),
    [
        (FireflyAuthenticationError, "invalid_auth"),
        (FireflyConnectionError, "cannot_connect"),
        (FireflyTimeoutError, "timeout_connect"),
        (Exception("Some other error"), "unknown"),
    ],
)
async def test_full_flow_reconfigure_exceptions(
    hass: HomeAssistant,
    mock_firefly_client: AsyncMock,
    mock_setup_entry: MagicMock,
    mock_config_entry: MockConfigEntry,
    exception: Exception,
    reason: str,
) -> None:
    """Test the reconfigure flow surfaces errors and can recover afterwards."""
    mock_config_entry.add_to_hass(hass)
    result = await mock_config_entry.start_reconfigure_flow(hass)

    mock_firefly_client.get_about.side_effect = exception
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=USER_INPUT_RECONFIGURE
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": reason}

    mock_firefly_client.get_about.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=USER_INPUT_RECONFIGURE
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_URL] == "https://new_domain:9000/"
    assert len(mock_setup_entry.mock_calls) == 1
