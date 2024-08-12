"""Config flow to configure Dreo."""  # noqa: EXE002

import hashlib
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from hscloud.hscloud import HsCloud
from hscloud.hscloudexception import HsCloudBusinessException, HsCloudException

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


class DreoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Dreo config flow."""

    @callback
    def _show_form(self, errors=None):  # noqa: ANN001, ANN202
        """Show form to the user."""
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors if errors else {}
        )

    async def async_step_user(self, user_input=None):  # noqa: ANN001, ANN201
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            return self._show_form()

        username = user_input[CONF_USERNAME]
        password = hashlib.md5(user_input[CONF_PASSWORD].encode("UTF-8")).hexdigest()  # noqa: S324

        manager = HsCloud(username, password)
        try:
            await self.hass.async_add_executor_job(manager.login)

        except HsCloudException:
            return self._show_form(errors={"base": "cannot_connect"})

        except HsCloudBusinessException:
            return self._show_form(errors={"base": "invalid_auth"})

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return self._show_form(errors={"base": "unknown"})

        return self.async_create_entry(
            title=username,
            data={CONF_USERNAME: username, CONF_PASSWORD: password},
        )
