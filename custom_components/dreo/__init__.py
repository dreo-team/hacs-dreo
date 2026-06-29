"""Dreo for Integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    Platform,
)
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from pydreo.client import DreoClient
from pydreo.exceptions import DreoBusinessException, DreoException

from .const import DEFAULT_SCAN_INTERVAL, DreoEntityConfigSpec
from .coordinator import DreoDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

type DreoConfigEntry = ConfigEntry["DreoData"]

PLATFORMS = [
    Platform.CLIMATE,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


@dataclass
class DreoData:
    """Dreo Data."""

    client: DreoClient
    devices: list[dict[str, Any]]
    coordinators: dict[str, DreoDataUpdateCoordinator]


async def async_login(
    hass: HomeAssistant, username: str, password: str
) -> tuple[DreoClient, list[dict[str, Any]]]:
    """Log into Dreo and return client and device data."""
    client = DreoClient(username, password)

    def setup_client() -> list[dict[str, Any]]:
        client.login()
        return client.get_devices()

    invalid_auth_msg = "Invalid username or password"
    try:
        devices = await hass.async_add_executor_job(setup_client)
    except DreoBusinessException as ex:
        raise ConfigEntryAuthFailed(invalid_auth_msg) from ex
    except DreoException as ex:
        error_msg = f"Error communicating with Dreo API: {ex}"
        raise ConfigEntryNotReady(error_msg) from ex

    return client, devices


async def async_setup_entry(hass: HomeAssistant, config_entry: DreoConfigEntry) -> bool:
    """Set up Dreo from as config entry."""
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    client, devices = await async_login(hass, username, password)
    coordinators: dict[str, DreoDataUpdateCoordinator] = {}

    scan_interval = int(
        config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    for device in devices:
        await async_setup_device_coordinator(
            hass, client, device, coordinators, scan_interval
        )

    config_entry.runtime_data = DreoData(client, devices, coordinators)

    config_entry.async_on_unload(config_entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    for coordinator in coordinators.values():
        if coordinator.data is not None:
            _LOGGER.debug(
                "Triggering state update for device %s after entity creation",
                coordinator.device_id,
            )
            coordinator.async_update_listeners()

    return True


async def async_update_options(
    hass: HomeAssistant, config_entry: DreoConfigEntry
) -> None:
    """Reload the entry when options change so the new scan interval applies."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_setup_device_coordinator(
    hass: HomeAssistant,
    client: DreoClient,
    device: dict[str, Any],
    coordinators: dict[str, DreoDataUpdateCoordinator],
    scan_interval: int = DEFAULT_SCAN_INTERVAL,
) -> None:
    """Set up coordinator for a single device."""
    device_model = device.get("model")
    device_id = device.get("deviceSn")
    device_type = device.get("deviceType")
    model_config = device.get(DreoEntityConfigSpec.TOP_CONFIG, {})
    initial_state = device.get("state")

    if not device_id or not device_model or not device_type:
        return

    if model_config is None:
        _LOGGER.warning("Model config is not available for model %s", device_model)
        return

    if device_id in coordinators:
        return

    coordinator = DreoDataUpdateCoordinator(
        hass, client, device_id, device_type, model_config, scan_interval
    )

    if coordinator.data_processor is None:
        return

    if initial_state:
        _LOGGER.debug("Using initial state from device list for %s", device_id)
        try:
            processed_data = coordinator.data_processor(initial_state, model_config)
            coordinator.async_set_updated_data(processed_data)
            _LOGGER.debug("Initial state set for %s", device_id)
        except (ValueError, KeyError, TypeError) as ex:
            _LOGGER.warning(
                "Failed to process initial state for %s: %s; will fetch fresh",
                device_id,
                ex,
            )
            await coordinator.async_request_refresh()
    else:
        await coordinator.async_config_entry_first_refresh()

    coordinators[device_id] = coordinator


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
