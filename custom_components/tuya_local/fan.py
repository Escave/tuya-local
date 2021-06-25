"""
Setup for different kinds of Tuya fan devices
"""
import logging

from . import DOMAIN
from .const import (
    CONF_FAN,
    CONF_DEVICE_ID,
    CONF_TYPE,
    CONF_TYPE_AUTO,
)
from .generic.fan import TuyaLocalFan
from .helpers.device_config import config_for_legacy_use

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Tuya device according to its type."""
    data = hass.data[DOMAIN][discovery_info[CONF_DEVICE_ID]]
    device = data["device"]

    if discovery_info[CONF_TYPE] == CONF_TYPE_AUTO:
        raise ValueError(f"Device type for {device.name} not resolved before fan init")

    cfg = config_for_legacy_use(discovery_info[CONF_TYPE])
    ecfg = cfg.primary_entity
    if ecfg.entity != "fan":
        for ecfg in cfg.secondary_entities():
            if ecfg.entity == "fan":
                break
        if ecfg.entity != "fan":
            raise ValueError(f"{device.name} does not support use as a fan device.")

    if ecfg.deprecated:
        _LOGGER.warning(ecfg.deprecation_message)

    data[CONF_FAN] = TuyaLocalFan(device, ecfg)

    async_add_entities([data[CONF_FAN]])
    _LOGGER.debug(f"Adding fan device for {discovery_info[CONF_TYPE]}")


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    discovery_info = {
        CONF_DEVICE_ID: config[CONF_DEVICE_ID],
        CONF_TYPE: config[CONF_TYPE],
    }
    await async_setup_platform(hass, {}, async_add_entities, discovery_info)
