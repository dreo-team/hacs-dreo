"""Config flow to configure Dreo."""

from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from pydreo.client import DreoClient
from pydreo.exceptions import DreoBusinessException, DreoException

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


class DreoFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Dreo config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,  # noqa: ARG004
    ) -> DreoOptionsFlowHandler:
        """Get the options flow for this handler."""
        return DreoOptionsFlowHandler()

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using MD5 (API requirement)."""
        return hashlib.md5(password.encode("UTF-8")).hexdigest()  # noqa: S324

    async def _validate_login(
        self, username: str, password: str
    ) -> tuple[bool, str | None]:
        """Validate login credentials."""
        client = DreoClient(username, password)

        try:
            await self.hass.async_add_executor_job(client.login)
        except DreoException:
            return False, "cannot_connect"
        except DreoBusinessException:
            return False, "invalid_auth"
        return True, None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input:
            username = user_input[CONF_USERNAME]
            hashed_password = self._hash_password(user_input[CONF_PASSWORD])

            await self.async_set_unique_id(username.lower())
            self._abort_if_unique_id_configured()

            is_valid, error = await self._validate_login(username, hashed_password)
            if is_valid:
                return self.async_create_entry(
                    title=username,
                    data={CONF_USERNAME: username, CONF_PASSWORD: hashed_password},
                )
            errors["base"] = error if error else "unknown_error"
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class DreoOptionsFlowHandler(OptionsFlow):
    """Handle Dreo integration options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the Dreo options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=5,
                        unit_of_measurement="seconds",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema)
