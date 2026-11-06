# Firefly III for Home Assistant

<img src="https://brands.home-assistant.io/_/firefly_iii/icon.png" alt="Firefly III icon" width="96" height="96" align="right">

[![Marketplace](https://img.shields.io/badge/Marketplace-Custom-41BDF5.svg)](https://www.home-assistant.io/integrations/marketplace/)
[![Release](https://img.shields.io/github/v/release/Passific/ha-firefly-iii)](https://github.com/Passific/ha-firefly-iii/releases)
[![Downloads](https://img.shields.io/github/downloads/passific/ha-firefly-iii/total)](https://github.com/Passific/ha-firefly-iii/releases)
[![License](https://img.shields.io/github/license/Passific/ha-firefly-iii)](LICENSE)
[![Validate](https://github.com/Passific/ha-firefly-iii/actions/workflows/ci.yml/badge.svg)](https://github.com/Passific/ha-firefly-iii/actions/workflows/ci.yml)

A Home Assistant custom integration that connects to your [Firefly III](https://www.firefly-iii.org/) instance and exposes your accounts, budgets, categories and subscriptions as sensors.

> [!IMPORTANT]
> Home Assistant core already ships a built-in `firefly_iii` integration. Because this custom integration uses the **same domain** (`firefly_iii`), installing it will **override the core integration** — Home Assistant always prefers a `custom_components/firefly_iii` folder over the built-in one. Uninstalling this custom integration (and restarting) restores the stock core integration.

## Features

- Account balance sensors
- Budget spent / limit / remaining sensors
- Category earned / spent sensors
- Subscription (bill) amount, next expected and last paid sensors
- Config flow (UI based setup, no YAML required)
- Reauthentication and reconfiguration support

## Installation

### Marketplace (recommended)

1. Go to **Settings > Marketplace**.
2. In the upper-right corner, select **Add from link**.
3. Add `https://github.com/Passific/ha-firefly-iii` under **GitHub link**.
4. Select **Add**.
5. Search for **Firefly III** in the Marketplace and install it.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=Passific&repository=ha-firefly-iii&category=integration)

### Manual

1. Download the latest release from the [releases page](https://github.com/Passific/ha-firefly-iii/releases).
2. Copy the `custom_components/firefly_iii` folder into your Home Assistant `config/custom_components` directory.
3. Restart Home Assistant.

## Configuration

Configuration is done entirely through the Home Assistant UI.

1. Go to **Settings > Devices & Services > Add Integration**.
2. Search for **Firefly III**.
3. Enter the URL of your Firefly III instance and a personal access token.
   - You can create a personal access token in Firefly III under **Options > Remote access and tokens**.

| Field | Description |
| ----- | ----------- |
| URL | The base URL of your Firefly III instance, e.g. `https://firefly.example.com` |
| Access token | A Firefly III personal access token |
| Verify SSL | Whether to verify the SSL certificate of the Firefly III instance |

## Removal

1. Go to **Settings > Marketplace**.
2. Open the page of the repository.
3. Select the three dots ⋮ menu in the upper-right corner, then select **Uninstall**.
   - If the integration is still configured, select **View integration** to remove the integration setup yourself, or **Delete and uninstall** to remove the setup and uninstall the integration in one step.
4. Confirm.

## Supported devices and functions

This integration talks to a single Firefly III instance (self-hosted or hosted) over its REST API using a personal access token. There is no physical device involved — one config entry represents one Firefly III instance, grouped into four logical devices: **Accounts**, **Categories**, **Budgets** and **Subscriptions**.

For each item Firefly III reports, the integration creates:

| Firefly III object | Entities created |
| ------------------- | ----------------- |
| Asset account | Current balance sensor |
| Category | Net earned/spent sensor (current month) |
| Budget | Spent, limit and remaining sensors (current month) |
| Bill / subscription | Expected amount, next expected date, last paid date |
| _(aggregate)_ | Total expected and already-paid across all active subscriptions (current month) |

New accounts, categories, budgets and bills created in Firefly III are picked up automatically on the next refresh — no reload is required.

## Data updates

Data is polled every 5 minutes via the Firefly III REST API. There is currently no push/webhook mechanism, so changes made in Firefly III can take up to 5 minutes to appear in Home Assistant.

## Use cases

- Track account balances and net worth on a Home Assistant dashboard.
- Get notified (via automations) when a budget is close to its limit or a subscription is about to be charged.
- Combine with the Energy dashboard or custom cards to visualize monthly spending trends.

## Examples

A simple automation that notifies when a budget is nearly exhausted:

```yaml
automation:
  - alias: "Notify when grocery budget is almost spent"
    trigger:
      - platform: numeric_state
        entity_id: sensor.budgets_groceries_remaining
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Groceries budget has less than 20 left this month."
```

## Known limitations

- Only asset accounts are exposed as balance sensors; expense/revenue/liability accounts are not currently supported.
- Budget/category/subscription figures are always scoped to the current calendar month.
- There is no way to trigger an immediate refresh from the Firefly III side (no webhooks); Home Assistant always polls.

## Troubleshooting

- **"Failed to connect" during setup**: verify the URL is reachable from Home Assistant and includes the scheme (`https://...`). If using a self-signed certificate, try disabling "Verify SSL".
- **"Invalid authentication"**: the personal access token is wrong, expired, or was revoked — generate a new one in Firefly III under **Options > Remote access and tokens** and use the reauthentication flow.
- **Entities show as unavailable**: check **Settings > Devices & Services > Firefly III** for repair/error notifications, and review the Home Assistant logs for the `custom_components.firefly_iii` logger.
- **Diagnostics**: you can download config entry diagnostics from **Settings > Devices & Services > Firefly III > ⋮ > Download diagnostics** to help with bug reports (sensitive data such as the URL and token are redacted).

## Contributing

Issues and pull requests are welcome at [github.com/Passific/ha-firefly-iii](https://github.com/Passific/ha-firefly-iii).

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
