"""Parse the value formats used by the MeteoLux forecast."""

import datetime
import logging

from .const import WIND_BEARINGS

_LOGGER = logging.getLogger(__name__)


def parse_range(value: str | float | None) -> float | None:
    """Return the upper bound of a range like "20-30", or the value itself."""
    if isinstance(value, int | float):
        return float(value)
    if not value:
        return None
    try:
        return float(value.rpartition("-")[2])
    except ValueError:
        _LOGGER.debug("Could not parse value %s", value)
        return None


def parse_temperature(temperature: int | list[int]) -> float | None:
    """Return the temperature, or the upper bound of a temperature range."""
    if isinstance(temperature, list):
        return float(max(temperature)) if temperature else None
    return float(temperature)


def parse_precipitation(rain: str | int, snow: str | int) -> float | None:
    """Return the upper bound of the expected rain or snow, whichever is higher."""
    values = [v for v in (parse_range(rain), parse_range(snow)) if v is not None]
    return max(values, default=None)


def parse_wind_bearing(direction: str) -> float | None:
    """Return the wind bearing in degrees for a compass direction."""
    return WIND_BEARINGS.get(direction.strip().upper())


def localize(value: datetime.datetime, time_zone: datetime.tzinfo) -> datetime.datetime:
    """Attach the API time zone to a naive forecast date."""
    if value.tzinfo is None:
        return value.replace(tzinfo=time_zone)
    return value
