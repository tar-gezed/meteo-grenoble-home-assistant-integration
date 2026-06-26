"""Config flow for Météo-Grenoble.com integration."""
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant import data_entry_flow

from .const import DOMAIN, DEFAULT_NAME


class MeteoGrenobleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Météo-Grenoble.com."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
