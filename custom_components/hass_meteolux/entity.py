"""Shared entity helpers for the MeteoLux integration."""

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import MeteoluxDataUpdateCoordinator


def base_unique_id(coordinator: MeteoluxDataUpdateCoordinator) -> str:
    """Return the unique ID prefix, as used since the first version."""
    city = coordinator.data.weather.city
    return f"{city.lat},{city.long}"


def device_info(coordinator: MeteoluxDataUpdateCoordinator) -> DeviceInfo:
    """Return the device info of the place."""
    entry = coordinator.config_entry
    if TYPE_CHECKING:
        assert entry.unique_id is not None
    return DeviceInfo(
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, entry.unique_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name=entry.title,
    )
