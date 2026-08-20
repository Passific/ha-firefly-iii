"""The Firefly III integration."""

from collections.abc import Callable
from functools import partial
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .coordinator import FireflyConfigEntry, FireflyDataUpdateCoordinator

_PLATFORMS: list[Platform] = [Platform.SENSOR]

_ENTITY_ID_SUFFIX_MIGRATIONS: tuple[tuple[str, Callable[[str], str]], ...] = (
    ("_account_balance", lambda entity_name: f"accounts_{entity_name}"),
    ("_earned_spent", lambda entity_name: f"categories_{entity_name}"),
    (
        "_budget_limit",
        lambda entity_name: f"budgets_{entity_name}_limit",
    ),
    (
        "_budget_remaining",
        lambda entity_name: f"budgets_{entity_name}_remaining",
    ),
    ("_budget", lambda entity_name: f"budgets_{entity_name}_spent"),
    (
        "_expected_amount",
        lambda entity_name: f"subscriptions_{entity_name}_expected_amount",
    ),
    (
        "_next_expected",
        lambda entity_name: f"subscriptions_{entity_name}_next_expected",
    ),
    ("_last_paid", lambda entity_name: f"subscriptions_{entity_name}_last_paid"),
)


def _async_migrate_legacy_entity_id(entity_id: str) -> str | None:
    """Migrate a legacy Firefly III entity id to a grouped entity id."""
    if not entity_id.startswith("sensor."):
        return None

    object_id = entity_id.removeprefix("sensor.")
    if object_id == "total_expected_subscriptions":
        return "sensor.subscriptions_total_expected"
    if object_id == "already_paid_subscriptions":
        return "sensor.subscriptions_already_paid"

    for suffix, migrate in _ENTITY_ID_SUFFIX_MIGRATIONS:
        if object_id.endswith(suffix):
            return f"sensor.{migrate(object_id.removesuffix(suffix))}"

    return None


@callback
def _async_migrate_entity_entry(
    entity_entry: er.RegistryEntry,
) -> dict[str, Any] | None:
    """Migrate legacy Firefly III entity registry entries."""
    if (new_entity_id := _async_migrate_legacy_entity_id(entity_entry.entity_id)) is None:
        return None

    if new_entity_id == entity_entry.entity_id:
        return None

    return {"new_entity_id": new_entity_id}


@callback
def _async_migrate_legacy_unique_id(
    entry_id: str, entity_entry: er.RegistryEntry
) -> dict[str, Any] | None:
    """Migrate unique_ids that were built from the (always-empty) config entry unique_id."""
    if entity_entry.unique_id is None or not entity_entry.unique_id.startswith(
        "None_"
    ):
        return None

    return {"new_unique_id": f"{entry_id}{entity_entry.unique_id.removeprefix('None')}"}


@callback
def _async_remove_orphaned_devices(hass: HomeAssistant, entry_id: str) -> None:
    """Remove Firefly III devices without entities for this config entry."""
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    for device_entry in dr.async_entries_for_config_entry(device_registry, entry_id):
        if er.async_entries_for_device(
            entity_registry,
            device_entry.id,
            include_disabled_entities=True,
        ):
            continue
        device_registry.async_remove_device(device_entry.id)


async def async_setup_entry(hass: HomeAssistant, entry: FireflyConfigEntry) -> bool:
    """Set up Firefly III from a config entry."""

    await er.async_migrate_entries(
        hass, entry.entry_id, partial(_async_migrate_legacy_unique_id, entry.entry_id)
    )
    await er.async_migrate_entries(hass, entry.entry_id, _async_migrate_entity_entry)

    coordinator = FireflyDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    _async_remove_orphaned_devices(hass, entry.entry_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: FireflyConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
