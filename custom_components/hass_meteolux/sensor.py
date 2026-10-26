"""Sensor platform for the MeteoLux integration."""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import (
    MeteoluxConfigEntry,
    MeteoluxData,
    MeteoluxDataUpdateCoordinator,
)
from .entity import base_unique_id, device_info
from .parsing import parse_range, parse_temperature

# The coordinator handles all updates.
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class MeteoluxSensorEntityDescription(SensorEntityDescription):
    """Describes a MeteoLux sensor entity."""

    value_fn: Callable[[MeteoluxData], float | None]


SENSOR_TYPES: tuple[MeteoluxSensorEntityDescription, ...] = (
    MeteoluxSensorEntityDescription(
        key="pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.observation.pressure,
    ),
    MeteoluxSensorEntityDescription(
        key="wind_speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: parse_range(data.weather.forecast.current.wind.speed),
    ),
    MeteoluxSensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: parse_temperature(
            data.weather.forecast.current.temperature.temperature
        ),
    ),
    MeteoluxSensorEntityDescription(
        key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.observation.humidity,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MeteoluxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the MeteoLux sensor platform."""
    async_add_entities(
        MeteoluxSensor(entry.runtime_data, description) for description in SENSOR_TYPES
    )


class MeteoluxSensor(CoordinatorEntity[MeteoluxDataUpdateCoordinator], SensorEntity):
    """A MeteoLux sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    entity_description: MeteoluxSensorEntityDescription

    def __init__(
        self,
        coordinator: MeteoluxDataUpdateCoordinator,
        description: MeteoluxSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{base_unique_id(coordinator)}_{description.key}"
        self._attr_device_info = device_info(coordinator)

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.entity_description.value_fn(self.coordinator.data)
