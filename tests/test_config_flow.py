"""Tests for the MeteoLux config flow."""

from unittest.mock import MagicMock

import httpx
from meteolux.exceptions import NotFoundError
import pydantic
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.hass_meteolux.const import CONF_CITY, CONF_CITY_ID, DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_full_flow(hass: HomeAssistant, mock_client: MagicMock) -> None:
    """Test picking a place creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    selector = result["data_schema"].schema[CONF_CITY]
    assert [option["label"] for option in selector.config["options"]] == [
        "Ettelbruck",
        "Luxembourg",
        "Mamer",
    ]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CITY: "457"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Mamer"
    assert result["data"] == {
        CONF_LATITUDE: 49.628424,
        CONF_LONGITUDE: 6.025544,
        CONF_CITY_ID: 457,
    }
    assert result["result"].unique_id == "49.628424, 6.025544"


async def test_already_configured(
    hass: HomeAssistant, mock_client: MagicMock, mock_config_entry: MockConfigEntry
) -> None:
    """Test a place can only be added once."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_CITY: "457"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(httpx.ConnectError("boom"), id="network"),
        pytest.param(NotFoundError("gone"), id="not_found"),
        pytest.param(pydantic.ValidationError.from_exception_data("x", []), id="data"),
    ],
)
async def test_cannot_connect(
    hass: HomeAssistant, mock_client: MagicMock, error: Exception
) -> None:
    """Test the flow aborts when the places can't be fetched."""
    mock_client.get_bookmarks.side_effect = error
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"
