# Firefly III for Home Assistant

<img src="https://brands.home-assistant.io/_/firefly_iii/icon.png" alt="Firefly III icon" width="96" height="96" align="right">

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Passific/ha-firefly-iii)](https://github.com/Passific/ha-firefly-iii/releases)
[![License](https://img.shields.io/github/license/Passific/ha-firefly-iii)](LICENSE)
[![Validate](https://github.com/Passific/ha-firefly-iii/actions/workflows/validate.yaml/badge.svg)](https://github.com/Passific/ha-firefly-iii/actions/workflows/validate.yaml)

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

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS > Integrations > ⋮ > Custom repositories**.
3. Add `https://github.com/Passific/ha-firefly-iii` as an **Integration** repository.
4. Search for **Firefly III** in HACS and install it.
5. Restart Home Assistant.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Passific&repository=ha-firefly-iii&category=integration)

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

Remove the integration from **Settings > Devices & Services**, then (optionally) delete the `custom_components/firefly_iii` folder from your Home Assistant configuration directory. Once the folder is removed and Home Assistant is restarted, the core `firefly_iii` integration (if available in your version) will be used instead.

## Contributing

Issues and pull requests are welcome at [github.com/Passific/ha-firefly-iii](https://github.com/Passific/ha-firefly-iii).

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
