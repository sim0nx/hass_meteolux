"""Data update coordinator for the MeteoLux integration."""

from dataclasses import dataclass
import datetime
import logging
from typing import TYPE_CHECKING

import httpx
from meteolux import AsyncMeteoLuxClient
from meteolux.exceptions import MeteoLuxError
from meteolux.models import WeatherResponse
import pydantic

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_TIME_ZONE,
    DOMAIN,
    LANGCODE,
    OBSERVATION_HUMIDITY,
    OBSERVATION_PRESSURE,
    OBSERVATION_VISIBILITY,
    SCAN_INTERVAL,
    VISIBILITY_MAX_METERS,
)

_LOGGER = logging.getLogger(__name__)

# The client lets httpx and pydantic errors through, only 404s are wrapped.
API_ERRORS = (MeteoLuxError, httpx.HTTPError, pydantic.ValidationError)

type MeteoluxConfigEntry = ConfigEntry[MeteoluxDataUpdateCoordinator]


@dataclass
class ObservationData:
    """Latest observations of the Findel airport station."""

    pressure: float | None = None
    humidity: float | None = None
    visibility_km: float | None = None


@dataclass
class MeteoluxData:
    """Data returned by the coordinator."""

    weather: WeatherResponse
    observation: ObservationData


def parse_observations(values: dict[str, float | None]) -> ObservationData:
    """Pick the observations used by the integration."""
    visibility = values.get(OBSERVATION_VISIBILITY)
    if visibility is not None:
        visibility = 10.0 if visibility >= VISIBILITY_MAX_METERS else visibility / 1000
    return ObservationData(
        pressure=values.get(OBSERVATION_PRESSURE),
        humidity=values.get(OBSERVATION_HUMIDITY),
        visibility_km=visibility,
    )


class MeteoluxDataUpdateCoordinator(DataUpdateCoordinator[MeteoluxData]):
    """Class to manage fetching MeteoLux data from the API."""

    config_entry: MeteoluxConfigEntry
    time_zone: datetime.tzinfo

    def __init__(self, hass: HomeAssistant, config_entry: MeteoluxConfigEntry) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api_client = AsyncMeteoLuxClient(session=get_async_client(hass))

    async def _async_setup(self) -> None:
        """Load the time zone of the forecast dates."""
        time_zone = await dt_util.async_get_time_zone(API_TIME_ZONE)
        if TYPE_CHECKING:
            assert time_zone is not None
        self.time_zone = time_zone

    async def _async_update_data(self) -> MeteoluxData:
        """Fetch the forecast and the latest observations."""
        try:
            observations = await self.api_client.get_observations_hvd()
            weather = await self.api_client.get_weather(
                langcode=LANGCODE,
                lat=float(self.config_entry.data[CONF_LATITUDE]),
                long=float(self.config_entry.data[CONF_LONGITUDE]),
            )
        except API_ERRORS as err:
            raise UpdateFailed(f"Error fetching MeteoLux data: {err}") from err

        return MeteoluxData(
            weather=weather,
            observation=parse_observations(
                {item.id: item.value for item in observations.data}
            ),
        )
