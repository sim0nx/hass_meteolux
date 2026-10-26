"""Tests for the MeteoLux value parsing."""

import pytest

from custom_components.hass_meteolux.const import CONDITION_CLASSES
from custom_components.hass_meteolux.coordinator import parse_observations
from custom_components.hass_meteolux.parsing import (
    parse_precipitation,
    parse_range,
    parse_temperature,
    parse_wind_bearing,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20-30", 30.0),
        ("05-10", 10.0),
        ("0", 0.0),
        (0, 0.0),
        (2.5, 2.5),
        ("", None),
        (None, None),
        ("n/a", None),
    ],
)
def test_parse_range(value: str | float | None, expected: float | None) -> None:
    """Test ranges resolve to their upper bound."""
    assert parse_range(value) == expected


@pytest.mark.parametrize(
    ("temperature", "expected"),
    [(9, 9.0), ([10, 12], 12.0), ([-3, -1], -1.0), ([], None)],
)
def test_parse_temperature(
    temperature: int | list[int], expected: float | None
) -> None:
    """Test temperatures and temperature ranges."""
    assert parse_temperature(temperature) == expected


@pytest.mark.parametrize(
    ("rain", "snow", "expected"),
    [
        ("1-2", "0", 2.0),
        ("0", "1-3", 3.0),
        (0, 0, 0.0),
        ("", "", None),
    ],
)
def test_parse_precipitation(
    rain: str | int, snow: str | int, expected: float | None
) -> None:
    """Test rain or snow, whichever is higher, is used."""
    assert parse_precipitation(rain, snow) == expected


@pytest.mark.parametrize(
    ("direction", "expected"),
    [("N", 0), ("SO", 225), ("SW", 225), ("O", 270), ("no", 315), ("", None)],
)
def test_parse_wind_bearing(direction: str, expected: float | None) -> None:
    """Test French and English compass directions."""
    assert parse_wind_bearing(direction) == expected


@pytest.mark.parametrize(
    ("visibility", "expected"),
    [(9999, 10.0), (2500, 2.5), (None, None)],
)
def test_visibility(visibility: int | None, expected: float | None) -> None:
    """Test visibility is converted from metres to kilometres."""
    assert parse_observations({"svv": visibility}).visibility_km == expected


def test_condition_icons_unique() -> None:
    """Test no icon is mapped to two conditions."""
    codes = [code for codes in CONDITION_CLASSES.values() for code in codes]
    assert len(codes) == len(set(codes))
