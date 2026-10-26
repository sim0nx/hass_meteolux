"""Tests for the MeteoLux setup, weather and sensor entities."""

from unittest.mock import MagicMock

from freezegun.api import FrozenDateTimeFactory
import httpx
from meteolux.exceptions import NotFoundError
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from syrupy.assertion import SnapshotAssertion

from custom_components.hass_meteolux.const import CONF_CITY_ID, DOMAIN
from homeassistant.components.weather import (
    DOMAIN as WEATHER_DOMAIN,
    SERVICE_GET_FORECASTS,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

WEATHER_ENTITY_ID = "weather.mamer"
NOW = "2026-10-26 13:30:00+01:00"


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


@pytest.mark.usefixtures("mock_client")
async def test_weather_state(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the current conditions."""
    freezer.move_to(NOW)
    await _setup(hass, mock_config_entry)
    assert hass.states.get(WEATHER_ENTITY_ID) == snapshot


@pytest.mark.usefixtures("mock_client")
@pytest.mark.parametrize("forecast_type", ["hourly", "daily"])
async def test_forecast(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
    forecast_type: str,
) -> None:
    """Test past periods are left out and dates are in Luxembourg time."""
    freezer.move_to(NOW)
    await _setup(hass, mock_config_entry)
    result = await hass.services.async_call(
        WEATHER_DOMAIN,
        SERVICE_GET_FORECASTS,
        {"entity_id": WEATHER_ENTITY_ID, "type": forecast_type},
        blocking=True,
        return_response=True,
    )
    assert result == snapshot


@pytest.mark.usefixtures("mock_client", "entity_registry_enabled_by_default")
async def test_sensors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the sensor values."""
    await _setup(hass, mock_config_entry)
    states = {state.entity_id: state.state for state in hass.states.async_all("sensor")}
    assert states == snapshot


@pytest.mark.usefixtures("mock_client")
async def test_existing_entry(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
) -> None:
    """Entries and entities created by 0.1.x keep working."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Mamer",
        unique_id="49.628424, 6.025544",
        data={
            CONF_LATITUDE: "49.628424",
            CONF_LONGITUDE: "6.025544",
            CONF_CITY_ID: "457",
        },
    )
    entry.add_to_hass(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "49.628424, 6.025544")},
        name="hass_meteolux",
    )
    for domain, unique_id, object_id in (
        ("weather", "49.628424,6.025544", "hass_meteolux_mamer_2"),
        ("sensor", "49.628424,6.025544_humidity", "mamer_humidity"),
    ):
        entity_registry.async_get_or_create(
            domain,
            DOMAIN,
            unique_id,
            suggested_object_id=object_id,
            config_entry=entry,
            device_id=device.id,
        )

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert hass.states.get("weather.hass_meteolux_mamer_2").state == "rainy"
    assert hass.states.get("sensor.mamer_humidity").state == "88"
    assert device_registry.async_get(device.id).name == "Mamer"
    assert len(er.async_entries_for_config_entry(entity_registry, entry.entry_id)) == 5


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(httpx.ConnectError("boom"), id="network"),
        pytest.param(
            httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "https://x"),
                response=httpx.Response(500),
            ),
            id="http_error",
        ),
        pytest.param(NotFoundError("gone"), id="not_found"),
    ],
)
async def test_setup_retry(
    hass: HomeAssistant,
    mock_client: MagicMock,
    mock_config_entry: MockConfigEntry,
    error: Exception,
) -> None:
    """Test API errors put the entry into retry."""
    mock_client.get_weather.side_effect = error
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


@pytest.mark.usefixtures("mock_client")
async def test_unload(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test unloading the entry."""
    await _setup(hass, mock_config_entry)
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
