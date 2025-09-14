"""Config flow for the MeteoLux integration."""

from __future__ import annotations

import logging
from typing import Any

from meteolux import AsyncMeteoLuxClient
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import DOMAIN
import homeassistant.helpers.httpx_client

_LOGGER = logging.getLogger(__name__)


class MeteoluxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeteoLux."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        weather_data = None

        if not user_input:
            session = homeassistant.helpers.httpx_client.get_async_client(
                hass=self.hass
            )
            api_client = AsyncMeteoLuxClient(session=session)
            cities = await api_client.get_bookmarks(langcode="en")

            places_for_form: dict[str, str] = {}
            for city in cities.cities:
                citiy_key = f"{city.id};{city.name};{city.lat};{city.long}"
                places_for_form[citiy_key] = city.name

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("city"): vol.All(
                            vol.Coerce(str), vol.In(places_for_form)
                        )
                    }
                ),
            )

        city_id, city_name, city_lat, city_long = user_input["city"].split(";")

        await self.async_set_unique_id(f"{city_lat}, {city_long}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=city_name,
            data={
                CONF_LATITUDE: city_lat,
                CONF_LONGITUDE: city_long,
                "city_id": city_id,
            },
        )
