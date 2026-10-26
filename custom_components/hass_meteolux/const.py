"""Constants for the MeteoLux integration."""

import datetime

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_EXCEPTIONAL,
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
ATTRIBUTION = "Data provided by MeteoLux (Administration de la navigation aérienne)"
MODEL = "MeteoLux API backend"
MANUFACTURER = "Administration de la navigation aérienne"

CONF_CITY = "city"
CONF_CITY_ID = "city_id"

LANGCODE = "en"
SCAN_INTERVAL = datetime.timedelta(minutes=15)

# Forecast dates are naive local times in Luxembourg.
API_TIME_ZONE = "Europe/Luxembourg"

# Observation IDs of the Luxembourg Findel airport station, the only station
# in the API.
OBSERVATION_PRESSURE = "sqnh"
OBSERVATION_HUMIDITY = "su"
OBSERVATION_VISIBILITY = "svv"
# Visibility is reported in metres, capped at 9999 for 10 km or more.
VISIBILITY_MAX_METERS = 9999

# Icon IDs, see README_api.md. Each icon ID may appear only once.
CONDITION_CLASSES: dict[str, list[int]] = {
    ATTR_CONDITION_CLEAR_NIGHT: [0, 6, 7, 11, 16, 46],
    ATTR_CONDITION_CLOUDY: [4, 5, 10, 12, 13],
    ATTR_CONDITION_EXCEPTIONAL: [55, 56],
    ATTR_CONDITION_FOG: [14, 15],
    ATTR_CONDITION_HAIL: [28, 29, 35, 41],
    ATTR_CONDITION_LIGHTNING: [42, 57],
    ATTR_CONDITION_LIGHTNING_RAINY: [47, 48, 49, 50, 51, 52, 53, 58, 59],
    ATTR_CONDITION_PARTLYCLOUDY: [2, 3, 8, 9],
    ATTR_CONDITION_POURING: [23],
    ATTR_CONDITION_RAINY: [17, 18, 19, 20, 21, 22, 30, 31, 36, 37],
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

# Wind directions use French abbreviations (O = ouest), English ones are
# accepted as well.
WIND_BEARINGS: dict[str, float] = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSO": 202.5,
    "SSW": 202.5,
    "SO": 225,
    "SW": 225,
    "OSO": 247.5,
    "WSW": 247.5,
    "O": 270,
    "W": 270,
    "ONO": 292.5,
    "WNW": 292.5,
    "NO": 315,
    "NW": 315,
    "NNO": 337.5,
    "NNW": 337.5,
}
