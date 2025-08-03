"""Weather platform for the MeteoLux integration."""
from __future__ import annotations

import datetime
import logging
import typing
from typing import Any

from meteolux import AsyncMeteoLuxClient
from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature, ATTR_FORECAST_TIME, ATTR_FORECAST_CONDITION, ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_PRECIPITATION, ATTR_FORECAST_NATIVE_WIND_SPEED, ATTR_FORECAST_WIND_BEARING,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.const import UnitOfTemperature, CONF_NAME, UnitOfPrecipitationDepth, UnitOfPressure, UnitOfSpeed, \
    UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, CONDITION_MAP
from . import MeteoluxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MeteoLux weather platform."""
    coordinator: MeteoluxDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MeteoluxWeather(coordinator, config_entry)])


class MeteoluxWeather(CoordinatorEntity[MeteoluxDataUpdateCoordinator], WeatherEntity):
    """Representation of a weather entity from MeteoLux."""

    _attr_attribution = "Data provided by MeteoLux"
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    _attr_has_entity_name = True
    _attr_supported_features = (WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY)

    def __init__(self, coordinator: MeteoluxDataUpdateCoordinator, config_entry: ConfigEntry) -> None:
        """Initialize the MeteoLux weather entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._city_name = self.coordinator.data.city.name
        self._attr_unique_id = f"{self.coordinator.data.city.lat},{self.coordinator.data.city.lat}"

        self.forecat_hourly: list[Forecast] | None = None
        self.forecat_daily: list[Forecast] | None = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._city_name

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        assert self.platform.config_entry and self.platform.config_entry.unique_id
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.platform.config_entry.unique_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=self.coordinator.name,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data:
            return None

        weather_icon_id = self.coordinator.data.forecast.current.icon.id
        return CONDITION_MAP.get(weather_icon_id, None)

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        if not self.coordinator.data:
            return None

        return self._get_temperature(self.coordinator.data.forecast.current.temperature.temperature)

    @staticmethod
    def _get_temperature(temperature: int | list[int]) -> float | None:
        if isinstance(temperature, list):
            temp = temperature[1]
        else:
            temp = temperature

        try:
            return float(temp)
        except (ValueError, TypeError):
            _LOGGER.warning("Could not parse temperature from API response: %s", temperature)
            return None

    @property
    def native_pressure(self):
        """Return the pressure."""
        return self.coordinator.data_observation.pressure

    @property
    def humidity(self):
        """Return the humidity."""
        return self.coordinator.data_observation.humidity

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        return self._get_wind_speed(self.coordinator.data.forecast.current.wind.speed)

    @staticmethod
    def _get_wind_speed(wind_speed: str) -> float:
        """Return the wind speed."""
        if '-' in wind_speed:
            return float(wind_speed.split('-')[1])

        return float(wind_speed)

    @property
    def native_wind_gust_speed(self):
        """Return the wind gust speed."""
        wind_gusts = self.coordinator.data.forecast.current.wind.gusts

        if wind_gusts is not None:
            return float(wind_gusts)

        return None

    @property
    def native_visibility(self):
        """Return the visibility."""
        return self.coordinator.data_observation.visibility

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self.coordinator.data.forecast.current.wind.direction

    @staticmethod
    def _get_precipitation(precipitation: str | None) -> float | None:
        """Precipitation can contain a range; this function returns the maximum value."""
        if precipitation is None or not precipitation:
            return None

        if '-' in precipitation:
            max_precipitation = float(precipitation.split('-')[1])
        else:
            max_precipitation = float(precipitation)

        return max_precipitation

    @staticmethod
    def _get_precipitation_rain_snow(rain: str | None, snow: str | None) -> float | None:
        """If either snow or rain is set, return whatever parsed value."""
        if (rain is None and snow is None) or not (rain or snow):
            return 0.0

        max_rain = MeteoluxWeather._get_precipitation(rain)
        max_snow = MeteoluxWeather._get_precipitation(snow)

        if max_rain is not None:
            return max_rain

        if max_snow is not None:
            return max_snow

        return None

    def _forecast(self, mode: typing.Literal['hourly', 'daily']) -> list[Forecast] | None:
        """Return the forecast data."""
        forecast_data: list[Forecast] = []
        today = datetime.datetime.now(tz=datetime.UTC)

        if mode == 'hourly':
            for hfc in self.coordinator.data.forecast.hourly:
                fc_dt = hfc.date.replace(tzinfo=datetime.UTC)

                if fc_dt < today:
                    # ignore past data
                    continue

                forecast_data.append(
                    Forecast(
                        datetime=fc_dt.isoformat(),
                        condition=CONDITION_MAP.get(hfc.icon.id, None),
                        native_temperature=self._get_temperature(hfc.temperature.temperature),
                        native_precipitation=self._get_precipitation_rain_snow(rain=hfc.rain, snow=hfc.snow),
                        native_wind_speed=self._get_wind_speed(hfc.wind.speed),
                        wind_bearing=hfc.wind.direction,
                    )
                )

        else:
            for dfc in self.coordinator.data.forecast.daily:
                fc_dt = dfc.date.replace(tzinfo=datetime.UTC)

                if fc_dt < today:
                    # ignore past data
                    continue

                forecast_data.append(
                    Forecast(
                        datetime=fc_dt.isoformat(),
                        condition=CONDITION_MAP.get(dfc.icon.id, None),
                        native_temperature=self._get_temperature(dfc.temperature_max.temperature),
                        native_templow=self._get_temperature(dfc.temperature_min.temperature),
                        uv_index=dfc.uv_index,
                        native_precipitation=self._get_precipitation_rain_snow(rain=dfc.rain, snow=dfc.snow),
                    )
                )

        return forecast_data

    async def async_forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast in native units."""
        return self._forecast('daily')

    async def async_forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast in native units."""
        return self._forecast('hourly')
