"""The MeteoLux integration."""
from __future__ import annotations

import dataclasses
from datetime import timedelta
import logging
from typing import Any
import homeassistant.helpers.httpx_client
import meteolux.models
from meteolux import AsyncMeteoLuxClient
from meteolux.exceptions import MeteoLuxError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_LATITUDE, CONF_LONGITUDE, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


_LOGGER = logging.getLogger(__name__)

DOMAIN = "hass_meteolux"

# The platforms this integration supports.
PLATFORMS: list[Platform] = [Platform.WEATHER]

# The scan interval for the MeteoLux API
SCAN_INTERVAL = timedelta(minutes=15)

@dataclasses.dataclass
class ObservationData:
    pressure: float | None = None
    humidity: float | None = None
    visibility: float | None = None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MeteoLux from a config entry."""

    coordinator = MeteoluxDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class MeteoluxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching MeteoLux data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the data update coordinator."""
        self.config_entry = config_entry
        session = homeassistant.helpers.httpx_client.get_async_client(hass=hass)
        self.api_client = AsyncMeteoLuxClient(session=session)
        self.data: meteolux.models.WeatherResponse | None = None
        self.data_observation = ObservationData()

        self.scan_interval = SCAN_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> meteolux.models.WeatherResponse:
        """Fetch data from MeteoLux API."""
        try:
            data_observation = await self.api_client.get_observations_hvd()

            for data in data_observation.data:
                if data.id == 'sqnh':
                    self.data_observation.pressure = data.value
                elif data.id == 'su':
                    self.data_observation.humidity = data.value
                elif data.id == 'svv':
                    if data.value == 9999:
                        self.data_observation.visibility = 10000
                    else:
                        self.data_observation.visibility = data.value

        except MeteoLuxError as err:
            raise UpdateFailed(f"Error fetching MeteoLux data: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching MeteoLux data")
            raise UpdateFailed(f"Unexpected error: {err}") from err

        try:
            return await self.api_client.get_weather(
                langcode="en",
                lat=self.config_entry.data.get(CONF_LATITUDE),
                long=self.config_entry.data.get(CONF_LONGITUDE),
            )
        except MeteoLuxError as err:
            raise UpdateFailed(f"Error fetching MeteoLux data: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching MeteoLux data")
            raise UpdateFailed(f"Unexpected error: {err}") from err
