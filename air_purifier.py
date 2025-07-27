air_purifier:
  - platform: template_air_purifier
    name: "Bedroom Purifier"
    unique_id: "bedroom_purifier"
    state_template: "{{ states('input_boolean.purifier_switch') }}"
    air_quality_template: "{{ states('sensor.bedroom_pm25') }}"
    fan_speed_template: "{{ states('input_number.purifier_fan_speed') }}"
    preset_mode_template: "{{ states('input_select.purifier_mode') }}"
    preset_modes:
      - auto
      - sleep
      - boost
    filter_life_template: "{{ states('sensor.purifier_filter_life') }}"
    filter_status_template: "{{ states('sensor.purifier_filter_status') }}"
    humidity_template: "{{ states('sensor.room_humidity') }}"
    temperature_template: "{{ states('sensor.room_temperature') }}"
    icon_template: "{{ 'mdi:air-purifier' }}"
    entity_picture_template: "{{ states('sensor.purifier_picture') }}"
    availability_template: "{{ states('binary_sensor.purifier_available') == 'on' }}"
    set_state:
      service: input_boolean.toggle
      data:
        entity_id: input_boolean.purifier_switch


# File: custom_components/template_air_purifier/air_purifier.py
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.template import Template
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import STATE_ON, STATE_OFF

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None):
    name = config.get("name")
    unique_id = config.get("unique_id")
    state_template = config.get("state_template")
    air_quality_template = config.get("air_quality_template")
    fan_speed_template = config.get("fan_speed_template")
    preset_mode_template = config.get("preset_mode_template")
    preset_modes = config.get("preset_modes", [])
    filter_life_template = config.get("filter_life_template")
    filter_status_template = config.get("filter_status_template")
    humidity_template = config.get("humidity_template")
    temperature_template = config.get("temperature_template")
    icon_template = config.get("icon_template")
    entity_picture_template = config.get("entity_picture_template")
    availability_template = config.get("availability_template")
    set_state = config.get("set_state")

    async_add_entities([
        TemplateAirPurifier(
            hass, name, unique_id, state_template, air_quality_template, set_state,
            fan_speed_template, preset_mode_template, preset_modes,
            filter_life_template, filter_status_template, humidity_template,
            temperature_template, icon_template, entity_picture_template, availability_template
        )
    ])


class TemplateAirPurifier(FanEntity):
    _attr_device_class = "air_purifier"
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE

    def __init__(
        self, hass, name, unique_id, state_template, air_quality_template, set_state,
        fan_speed_template, preset_mode_template, preset_modes,
        filter_life_template, filter_status_template, humidity_template,
        temperature_template, icon_template, entity_picture_template, availability_template
    ):
        self._hass = hass
        self._name = name
        self._unique_id = unique_id
        self._preset_modes = preset_modes

        self._state_template = Template(state_template, hass)
        self._air_quality_template = Template(air_quality_template, hass)
        self._fan_speed_template = Template(fan_speed_template, hass)
        self._preset_mode_template = Template(preset_mode_template, hass)
        self._filter_life_template = Template(filter_life_template, hass)
        self._filter_status_template = Template(filter_status_template, hass)
        self._humidity_template = Template(humidity_template, hass)
        self._temperature_template = Template(temperature_template, hass)
        self._icon_template = Template(icon_template, hass) if icon_template else None
        self._entity_picture_template = Template(entity_picture_template, hass) if entity_picture_template else None
        self._availability_template = Template(availability_template, hass) if availability_template else None

        self._set_state_service = set_state.get("service")
        self._set_state_data = set_state.get("data")

        self._state = None
        self._air_quality = None
        self._fan_speed = None
        self._preset_mode = None
        self._filter_life = None
        self._filter_status = None
        self._humidity = None
        self._temperature = None
        self._available = True
        self._icon = None
        self._entity_picture = None

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        return self._state == STATE_ON

    @property
    def percentage(self):
        try:
            return int(float(self._fan_speed))
        except (ValueError, TypeError):
            return None

    @property
    def preset_mode(self):
        return self._preset_mode

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def icon(self):
        return self._icon

    @property
    def entity_picture(self):
        return self._entity_picture

    @property
    def available(self):
        return self._available

    @property
    def extra_state_attributes(self):
        return {
            "air_quality": self._air_quality,
            "filter_life": self._filter_life,
            "filter_status": self._filter_status,
            "humidity": self._humidity,
            "temperature": self._temperature
        }

    async def async_turn_on(self, **kwargs):
        await self._call_set_state()

    async def async_turn_off(self, **kwargs):
        await self._call_set_state()

    async def _call_set_state(self):
        await self._hass.services.async_call(
            domain=self._set_state_service.split(".")[0],
            service=self._set_state_service.split(".")[1],
            service_data=self._set_state_data,
            blocking=True,
        )

    async def async_update(self):
        self._state = self._state_template.async_render()
        self._air_quality = self._air_quality_template.async_render()
        self._fan_speed = self._fan_speed_template.async_render()
        self._preset_mode = self._preset_mode_template.async_render()
        self._filter_life = self._filter_life_template.async_render()
        self._filter_status = self._filter_status_template.async_render()
        self._humidity = self._humidity_template.async_render()
        self._temperature = self._temperature_template.async_render()
        if self._icon_template:
            self._icon = self._icon_template.async_render()
        if self._entity_picture_template:
            self._entity_picture = self._entity_picture_template.async_render()
        if self._availability_template:
            self._available = self._availability_template.async_render().lower() == "true"
