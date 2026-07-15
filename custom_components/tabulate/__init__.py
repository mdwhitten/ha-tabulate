"""The Tabulate integration.

Exposes a `tabulate.add_receipt` action that forwards a scanned receipt image to
the companion Tabulate add-on. Designed for unattended callers (e.g. an Apple
Shortcut using VisionKit) via Home Assistant's authenticated service API.
"""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TabulateClient
from .const import (
    ATTR_CONTENT_TYPE,
    ATTR_FILENAME,
    ATTR_IMAGE_BASE64,
    ATTR_STORE_NAME_HINT,
    ATTR_WAIT_FOR_PROCESSING,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_CONTENT_TYPE,
    DEFAULT_FILENAME,
    DEFAULT_PORT,
    DOMAIN,
    MAX_UPLOAD_BYTES,
    SERVICE_ADD_RECEIPT,
)

_LOGGER = logging.getLogger(__name__)

TabulateConfigEntry = ConfigEntry[TabulateClient]

ADD_RECEIPT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_IMAGE_BASE64): cv.string,
        vol.Optional(ATTR_FILENAME, default=DEFAULT_FILENAME): cv.string,
        vol.Optional(ATTR_CONTENT_TYPE, default=DEFAULT_CONTENT_TYPE): cv.string,
        vol.Optional(ATTR_STORE_NAME_HINT): cv.string,
        vol.Optional(ATTR_WAIT_FOR_PROCESSING, default=True): cv.boolean,
    }
)


def _decode_image(raw: str) -> bytes:
    """Decode and size-check the base64 image payload."""
    # Tolerate data: URIs and whitespace/newlines from Shortcuts encoders.
    if "," in raw and raw.strip().startswith("data:"):
        raw = raw.split(",", 1)[1]
    try:
        image = base64.b64decode(raw, validate=False)
    except (binascii.Error, ValueError) as err:
        raise ServiceValidationError(
            f"image_base64 is not valid base64: {err}"
        ) from err
    if not image:
        raise ServiceValidationError("image_base64 decoded to an empty payload")
    if len(image) > MAX_UPLOAD_BYTES:
        raise ServiceValidationError(
            f"Image is {len(image)} bytes, exceeding the "
            f"{MAX_UPLOAD_BYTES}-byte limit"
        )
    return image


async def async_setup_entry(
    hass: HomeAssistant, entry: TabulateConfigEntry
) -> bool:
    """Set up Tabulate from a config entry."""
    client = TabulateClient(
        async_get_clientsession(hass),
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    entry.runtime_data = client

    async def _handle_add_receipt(call: ServiceCall) -> ServiceResponse:
        """Forward a receipt image to the Tabulate add-on."""
        image = _decode_image(call.data[ATTR_IMAGE_BASE64])
        filename = call.data[ATTR_FILENAME]
        content_type = call.data[ATTR_CONTENT_TYPE]
        store_hint = call.data.get(ATTR_STORE_NAME_HINT)

        if call.data[ATTR_WAIT_FOR_PROCESSING]:
            result: dict[str, Any] = await client.upload_receipt(
                image, filename, content_type, store_hint
            )
            return result

        # Fire-and-forget: return immediately so slow processing can't time out
        # the caller. The upload runs to completion in the background.
        hass.async_create_background_task(
            client.upload_receipt(image, filename, content_type, store_hint),
            name="tabulate_add_receipt",
        )
        return {"queued": True}

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_RECEIPT,
        _handle_add_receipt,
        schema=ADD_RECEIPT_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: TabulateConfigEntry
) -> bool:
    """Unload a config entry and remove the service."""
    hass.services.async_remove(DOMAIN, SERVICE_ADD_RECEIPT)
    return True
