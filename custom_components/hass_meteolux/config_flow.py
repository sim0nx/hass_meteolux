"""Config flow for the MeteoLux integration."""

import logging
from typing import Any

from meteolux import AsyncMeteoLuxClient
from meteolux.models import BookmarkCity
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_CITY, CONF_CITY_ID, DOMAIN, LANGCODE
from .coordinator import API_ERRORS

_LOGGER = logging.getLogger(__name__)


class MeteoluxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeteoLux."""

    VERSION = 1

    _cities: dict[str, BookmarkCity]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user pick one of the MeteoLux places."""
        if user_input is not None:
            city = self._cities[user_input[CONF_CITY]]
            # Same format as earlier versions, so places can't be added twice.
            await self.async_set_unique_id(f"{city.lat}, {city.long}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=city.name,
                data={
                    CONF_LATITUDE: city.lat,
                    CONF_LONGITUDE: city.long,
                    CONF_CITY_ID: city.id,
                },
            )

        client = AsyncMeteoLuxClient(session=get_async_client(self.hass))
        try:
            bookmarks = await client.get_bookmarks(langcode=LANGCODE)
        except API_ERRORS as err:
            _LOGGER.debug("Error fetching MeteoLux places: %s", err)
            return self.async_abort(reason="cannot_connect")

        self._cities = {str(city.id): city for city in bookmarks.cities}
        options = [
            SelectOptionDict(value=city_id, label=city.name)
            for city_id, city in sorted(
                self._cities.items(), key=lambda item: item[1].name
            )
        ]
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CITY): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
        )
