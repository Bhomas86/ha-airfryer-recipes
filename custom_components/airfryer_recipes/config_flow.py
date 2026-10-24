"""Config flow for the Airfryer Recipes recipe library.

This flow never connects to a physical air fryer and requires no credentials.
Device selection and sample-recipe imports will be added in later issues.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN, NAME


class AirfryerRecipesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure one local recipe library per Home Assistant instance."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for confirmation before creating a device-independent library."""
        if user_input is not None:
            return self.async_create_entry(title=NAME, data={})

        # HA shows a confirmation button without arbitrary input fields.
        # The manifest's single_config_entry flag blocks duplicate instances.
        self._set_confirm_only()
        return self.async_show_form(step_id="user")
