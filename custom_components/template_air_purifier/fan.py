"""Support for Template Air Purifier."""

import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
)
from homeassistant.components.template.template_entity import TemplateEntity
from homeassistant.components.template.const import CONF_AVAILABILITY_TEMPLATE
from homeassistant.const import (
    CONF_NAME,
    CONF_ICON_TEMPLATE,
    CONF_UNIQUE_ID,
)
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import ConfigType
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "template_air_purifier"
ENTITY_ID_FORMAT = DOMAIN + ".{}"

CONF_STATE_TEMPLATE = "state_template"
CONF_SET_STATE = "set_state"
CONF_HUMIDITY_TEMPLATE = "humidity_template"
CONF_TEMPERATURE_TEMPLATE = "temperature_template"
CONF_AIR_QUALITY_TEMPLATE = "air_quality_template"

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_STATE_TEMPLATE): cv.template,
        vol.Required(CONF_SET_STATE): cv.SCRIPT_SCHEMA,
        vol.Optional(CONF_AVAILABILITY_TEMPLATE): cv.template,
        vol.Optional(CONF_ICON_TEMPLATE): cv.template,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_HUMIDITY_TEMPLATE): cv.template,
        vol.Optional(CONF_TEMPERATURE_TEMPLATE): cv.template,
        vol.Optional(CONF_AIR_QUALITY_TEMPLATE): cv.template,
    }
)

async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info=None
):
    """Set up the Template Air Purifier."""
    async_add_entities([TemplateAirPurifier(hass, config)])

class TemplateAirPurifier(TemplateEntity, FanEntity, RestoreEntity):
    """Representation of a Template Air Purifier."""

    _attr_should_poll = False
    _attr_supported_features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF

    def __init__(self, hass: HomeAssistant, config: ConfigType):
        super().__init__(
            hass,
            availability_template=config.get(CONF_AVAILABILITY_TEMPLATE),
            icon_template=config.get(CONF_ICON_TEMPLATE),
            unique_id=config.get(CONF_UNIQUE_ID),
        )
        self.hass = hass
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, config[CONF_NAME], hass=hass
        )
        self._attr_name = config[CONF_NAME]
        self._state_template = config[CONF_STATE_TEMPLATE]
        self._humidity_template = config.get(CONF_HUMIDITY_TEMPLATE)
        self._temperature_template = config.get(CONF_TEMPERATURE_TEMPLATE)
        self._air_quality_template = config.get(CONF_AIR_QUALITY_TEMPLATE)
        self._set_state_script = config[CONF_SET_STATE]

    async def async_turn_on(self, **kwargs):
        await self.hass.services.async_call(
            self._set_state_script["service"].split(".")[0],
            self._set_state_script["service"].split(".")[1],
            self._set_state_script.get("data", {}),
            blocking=True,
        )

    async def async_turn_off(self, **kwargs):
        await self.async_turn_on()  # assuming toggle for simplicity

    @property
    def is_on(self):
        return self._state_template.async_render() == "on"

    @property
    def extra_state_attributes(self):
        attrs = {}
        if self._humidity_template:
            attrs["humidity"] = self._humidity_template.async_render()
        if self._temperature_template:
            attrs["temperature"] = self._temperature_template.async_render()
        if self._air_quality_template:
            attrs["air_quality"] = self._air_quality_template.async_render()
        return attrs
