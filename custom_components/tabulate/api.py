"""Thin async client for the Tabulate add-on's receipt API."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp

from homeassistant.exceptions import HomeAssistantError

from .const import PING_PATH, PING_TIMEOUT, UPLOAD_PATH, UPLOAD_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class TabulateConnectionError(HomeAssistantError):
    """Raised when the Tabulate add-on cannot be reached."""


class TabulateApiError(HomeAssistantError):
    """Raised when the Tabulate add-on returns an error response."""


class TabulateClient:
    """Talks to the Tabulate add-on over the internal Supervisor network."""

    def __init__(
        self, session: aiohttp.ClientSession, host: str, port: int
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._base_url = f"http://{host}:{port}"

    async def async_ping(self) -> None:
        """Verify the add-on API is reachable (used by the config flow)."""
        url = f"{self._base_url}{PING_PATH}"
        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=PING_TIMEOUT)
            ) as resp:
                if resp.status >= 400:
                    raise TabulateApiError(
                        f"Tabulate API returned HTTP {resp.status}"
                    )
        except (aiohttp.ClientError, TimeoutError) as err:
            raise TabulateConnectionError(
                f"Could not reach the Tabulate add-on at {self._base_url}: {err}"
            ) from err

    async def upload_receipt(
        self,
        image: bytes,
        filename: str,
        content_type: str,
        store_name_hint: str | None = None,
    ) -> dict[str, Any]:
        """Upload a receipt image and return the parsed ProcessingResult.

        The upstream endpoint is synchronous: this coroutine only resolves once
        OCR + Claude Vision + categorization have finished.
        """
        url = f"{self._base_url}{UPLOAD_PATH}"
        form = aiohttp.FormData()
        form.add_field(
            "file", image, filename=filename, content_type=content_type
        )
        if store_name_hint:
            form.add_field("store_name_hint", store_name_hint)

        try:
            async with self._session.post(
                url,
                data=form,
                timeout=aiohttp.ClientTimeout(total=UPLOAD_TIMEOUT),
            ) as resp:
                body = await resp.text()
                if resp.status != 200:
                    raise TabulateApiError(
                        f"Tabulate rejected the receipt (HTTP {resp.status}): "
                        f"{body[:300]}"
                    )
                try:
                    return json.loads(body)
                except json.JSONDecodeError as err:
                    raise TabulateApiError(
                        f"Tabulate returned an unparseable response: {err}"
                    ) from err
        except TabulateApiError:
            raise
        except (aiohttp.ClientError, TimeoutError) as err:
            raise TabulateConnectionError(
                f"Upload to the Tabulate add-on failed: {err}"
            ) from err
