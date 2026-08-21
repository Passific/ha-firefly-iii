"""Tests for the Firefly III config flow."""

from unittest.mock import AsyncMock, patch

from pyfirefly import (
    FireflyAuthenticationError,
    FireflyConnectionError,
    FireflyTimeoutError,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.firefly_iii.const import DOMAIN
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

USER_INPUT = {
    CONF_URL: "https://firefly.example.com",
    CONF_VERIFY_SSL: True,
    CONF_API_KEY: "test-token",
}


def _patch_firefly(side_effect=None):
    """Patch the pyfirefly client used by the config flow."""
    client = AsyncMock()
    if side_effect is not None:
        client.get_about.side_effect = side_effect
    return patch(
        "custom_components.firefly_iii.config_flow.Firefly", return_value=client
    )


async def test_user_flow_success(hass: HomeAssistant, mock_setup_entry) -> None:
    """A valid URL and token creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with _patch_firefly():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == USER_INPUT[CONF_URL]
    assert result["data"] == USER_INPUT


@pytest.mark.parametrize(
    ("exception", "expected_error"),
    [
        (FireflyConnectionError, "cannot_connect"),
        (FireflyAuthenticationError, "invalid_auth"),
        (FireflyTimeoutError, "timeout_connect"),
        (ValueError, "unknown"),
    ],
)
async def test_user_flow_errors(
    hass: HomeAssistant, exception: type[Exception], expected_error: str
) -> None:
    """Errors raised while validating input surface as form errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with _patch_firefly(side_effect=exception()):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": expected_error}


async def test_reauth_flow_success(hass: HomeAssistant, mock_setup_entry) -> None:
    """A successful reauth updates the existing config entry's token."""
    entry = MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=None)
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    assert result["step_id"] == "reauth_confirm"

    with _patch_firefly():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: "new-token"}
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_API_KEY] == "new-token"


async def test_reconfigure_flow_success(hass: HomeAssistant, mock_setup_entry) -> None:
    """A successful reconfigure updates the existing config entry."""
    entry = MockConfigEntry(domain=DOMAIN, data=USER_INPUT, unique_id=None)
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    assert result["step_id"] == "reconfigure"

    new_input = {**USER_INPUT, CONF_URL: "https://new.example.com"}
    with _patch_firefly():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], new_input
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_URL] == "https://new.example.com"
