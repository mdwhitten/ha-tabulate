"""Config flow for the Tabulate integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TabulateClient, TabulateConnectionError
from .const import ADDON_SLUG, CONF_HOST, CONF_PORT, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TabulateConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tabulate."""

    VERSION = 1

    async def _async_try_connect(self, host: str, port: int) -> str | None:
        """Return an error key if the add-on can't be reached, else None."""
        client = TabulateClient(
            async_get_clientsession(self.hass), host, port
        )
        try:
            await client.async_ping()
        except TabulateConnectionError:
            return "cannot_connect"
        except Exception:  # noqa: BLE001 - surface unexpected errors to the user
            _LOGGER.exception("Unexpected error connecting to Tabulate add-on")
            return "unknown"
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: auto-detect the add-on when possible."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        host = await self._async_resolve_addon_host()
        if host is not None and (
            await self._async_try_connect(host, DEFAULT_PORT) is None
        ):
            return self.async_create_entry(
                title="Tabulate",
                data={CONF_HOST: host, CONF_PORT: DEFAULT_PORT},
            )

        # Auto-detection unavailable or unreachable — fall back to manual entry.
        return await self.async_step_manual()

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual host/port entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            error = await self._async_try_connect(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if error is None:
                return self.async_create_entry(
                    title="Tabulate", data=user_input
                )
            errors["base"] = error

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )
        return self.async_show_form(
            step_id="manual", data_schema=schema, errors=errors
        )

    async def _async_resolve_addon_host(self) -> str | None:
        """Resolve the add-on's internal hostname via the Supervisor, if any."""
        try:
            from homeassistant.components.hassio import (
                get_supervisor_client,
                is_hassio,
            )
        except ImportError:
            return None

        if not is_hassio(self.hass):
            return None

        try:
            client = get_supervisor_client(self.hass)
            info = await client.addons.addon_info(ADDON_SLUG)
        except Exception:  # noqa: BLE001 - Supervisor optional; degrade to manual
            _LOGGER.debug("Could not resolve Tabulate add-on via Supervisor")
            return None

        return getattr(info, "hostname", None) or getattr(
            info, "ip_address", None
        )
