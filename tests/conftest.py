"""Fixtures for the MeteoLux tests."""

from collections.abc import Generator
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from meteolux.models import Bookmarks, ObservationResponse, WeatherResponse
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy.assertion import SnapshotAssertion

from custom_components.hass_meteolux.const import CONF_CITY_ID, DOMAIN
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations in all tests."""


@pytest.fixture(autouse=True)
async def set_tz(hass: HomeAssistant) -> None:
    """Use the Luxembourg time zone."""
    await hass.config.async_set_time_zone("Europe/Luxembourg")


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Use the Home Assistant extension regardless of plugin load order."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Enable entities that are disabled by default."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        new_callable=PropertyMock,
        return_value=True,
    ):
        yield


@pytest.fixture
def mock_client() -> Generator[MagicMock]:
    """Mock the MeteoLux API client."""
    client = MagicMock()
    client.get_bookmarks = AsyncMock(
        return_value=Bookmarks.model_validate(load_fixture("bookmarks.json"))
    )
    client.get_weather = AsyncMock(
        return_value=WeatherResponse.model_validate(load_fixture("weather.json"))
    )
    client.get_observations_hvd = AsyncMock(
        return_value=ObservationResponse.model_validate(
            load_fixture("observations.json")
        )
    )
    with (
        patch(
            "custom_components.hass_meteolux.coordinator.AsyncMeteoLuxClient",
            return_value=client,
        ),
        patch(
            "custom_components.hass_meteolux.config_flow.AsyncMeteoLuxClient",
            return_value=client,
        ),
    ):
        yield client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry as created by the current config flow."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Mamer",
        unique_id="49.628424, 6.025544",
        data={CONF_LATITUDE: 49.628424, CONF_LONGITUDE: 6.025544, CONF_CITY_ID: 457},
    )
