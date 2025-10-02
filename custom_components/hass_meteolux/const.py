"""Constants for the MeteoLux integration."""

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
)

DOMAIN = "hass_meteolux"
ATTRIBUTION = "Data provided by Administration de la navigation aérienne / MeteLux"
MODEL = "MeteoLux API backend"
MANUFACTURER = "Administration de la navigation aérienne"

# Inspired by meteo_france integration
CONDITION_CLASSES: dict[str, list[int]] = {
    ATTR_CONDITION_CLEAR_NIGHT: [0, 6, 7, 11, 16, 46],
    ATTR_CONDITION_CLOUDY: [4, 5, 10],
    ATTR_CONDITION_FOG: [14, 15],
    ATTR_CONDITION_HAIL: [28, 29, 35, 41],
    ATTR_CONDITION_LIGHTNING: [42, 47, 53, 57],
    ATTR_CONDITION_LIGHTNING_RAINY: [48, 49, 50, 51, 52, 53, 58, 59],
    ATTR_CONDITION_PARTLYCLOUDY: [2, 3, 8, 9],
    ATTR_CONDITION_POURING: [23],
    ATTR_CONDITION_RAINY: [17, 18, 19, 20, 21, 22, 23, 30, 31, 36, 37],
    ATTR_CONDITION_SNOWY: [25, 26, 33, 34, 39, 40],
    ATTR_CONDITION_SNOWY_RAINY: [24, 27, 32, 38, 43, 44, 45],
    ATTR_CONDITION_SUNNY: [1],
    ATTR_CONDITION_WINDY: [54],
}
CONDITION_MAP = {
    cond_code: cond_ha
    for cond_ha, cond_codes in CONDITION_CLASSES.items()
    for cond_code in cond_codes
}
