"""Support for MeteoLux sensor."""

from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MeteoluxDataUpdateCoordinator
from .const import ATTRIBUTION, DOMAIN, MANUFACTURER, MODEL


@dataclass(frozen=True, kw_only=True)
class MeteoLuxSensorEntityDescription(SensorEntityDescription):
    """Describes Meteo-France sensor entity."""

    data_path: str


SENSOR_TYPES: tuple[MeteoLuxSensorEntityDescription, ...] = (
    MeteoLuxSensorEntityDescription(
        key="pressure",
        name="Pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        data_path="data_observation.pressure",
    ),
    MeteoLuxSensorEntityDescription(
        key="wind_speed",
        name="Wind speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        data_path="data.forecast.current.wind.speed",
    ),
    MeteoLuxSensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        data_path="data.forecast.current.temperature.temperature",
    ),
    MeteoLuxSensorEntityDescription(
        key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        data_path="data_observation.humidity",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Meteo-France sensor platform."""
    coordinator: MeteoluxDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities: list[MeteoLuxSensor[Any]] = [
        MeteoLuxSensor(coordinator, description) for description in SENSOR_TYPES
    ]

    async_add_entities(entities, False)


class MeteoLuxSensor(CoordinatorEntity[MeteoluxDataUpdateCoordinator], SensorEntity):
    """Representation of a Meteo-France sensor."""

    entity_description: MeteoLuxSensorEntityDescription
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: MeteoluxDataUpdateCoordinator,
        description: MeteoLuxSensorEntityDescription,
    ) -> None:
        """Initialize the Meteo-France sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        city_name = self.coordinator.data.city.name
        self._attr_name = f"{city_name} {description.name}"
        self._attr_unique_id = f"{self.coordinator.data.city.lat},{self.coordinator.data.city.long}_{description.key}"

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
    def native_value(self):
        """Return the state."""
        path = self.entity_description.data_path.split(".")
        value = self.coordinator
        today = datetime.datetime.now(tz=datetime.UTC)

        for k in path:
            value = getattr(value, k)

        if self.entity_description.key == "wind_speed":
            if "-" in value:
                return float(value.split("-")[1])

            return float(value)

        return value
