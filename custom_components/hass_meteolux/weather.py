"""Weather platform for the MeteoLux integration."""

from meteolux.models import CurrentWeather, DailyWeather, HourlyWeather

from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, CONDITION_MAP
from .coordinator import MeteoluxConfigEntry, MeteoluxDataUpdateCoordinator
from .entity import base_unique_id, device_info
from .parsing import (
    localize,
    parse_precipitation,
    parse_range,
    parse_temperature,
    parse_wind_bearing,
)

# The coordinator handles all updates.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoluxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the MeteoLux weather platform."""
    async_add_entities([MeteoluxWeather(entry.runtime_data)])


class MeteoluxWeather(SingleCoordinatorWeatherEntity[MeteoluxDataUpdateCoordinator]):
    """Weather forecast for a MeteoLux place."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(self, coordinator: MeteoluxDataUpdateCoordinator) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._attr_unique_id = base_unique_id(coordinator)
        self._attr_device_info = device_info(coordinator)

    @property
    def _current(self) -> CurrentWeather:
        return self.coordinator.data.weather.forecast.current

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        return CONDITION_MAP.get(self._current.icon.id)

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return parse_temperature(self._current.temperature.temperature)

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature."""
        felt = self._current.temperature.felt
        return float(felt) if felt is not None else None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self.coordinator.data.observation.pressure

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self.coordinator.data.observation.humidity

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility."""
        return self.coordinator.data.observation.visibility_km

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return parse_range(self._current.wind.speed)

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed."""
        return parse_range(self._current.wind.gusts)

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        return parse_wind_bearing(self._current.wind.direction)

    def _forecast_entry(self, entry: HourlyWeather | DailyWeather) -> Forecast:
        return Forecast(
            datetime=localize(entry.date, self.coordinator.time_zone).isoformat(),
            condition=CONDITION_MAP.get(entry.icon.id),
            native_precipitation=parse_precipitation(entry.rain, entry.snow),
            native_wind_speed=parse_range(entry.wind.speed),
            native_wind_gust_speed=parse_range(entry.wind.gusts),
            wind_bearing=parse_wind_bearing(entry.wind.direction),
        )

    @callback
    def _async_forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast, starting with the period in progress."""
        entries = self.coordinator.data.weather.forecast.hourly
        time_zone = self.coordinator.time_zone
        now = dt_util.now()
        forecast: list[Forecast] = []
        # Each entry lasts until the next one starts.
        for entry, next_entry in zip(entries, [*entries[1:], None], strict=True):
            if next_entry and localize(next_entry.date, time_zone) <= now:
                continue
            forecast.append(
                self._forecast_entry(entry)
                | Forecast(
                    native_temperature=parse_temperature(entry.temperature.temperature)
                )
            )
        return forecast

    @callback
    def _async_forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast, starting today."""
        time_zone = self.coordinator.time_zone
        today = dt_util.now(time_zone).date()
        return [
            self._forecast_entry(entry)
            | Forecast(
                native_temperature=parse_temperature(entry.temperature_max.temperature),
                native_templow=parse_temperature(entry.temperature_min.temperature),
                uv_index=entry.uv_index,
            )
            for entry in self.coordinator.data.weather.forecast.daily
            if localize(entry.date, time_zone).date() >= today
        ]
