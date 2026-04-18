"""Data update coordinator for Dreo devices."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any, NoReturn

from homeassistant.components.climate import HVACMode
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.percentage import ranged_value_to_percentage
from pydreo.exceptions import DreoException

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from pydreo.client import DreoClient
from .const import (
    DOMAIN,
    DreoDeviceType,
    DreoDirective,
    DreoEntityConfigSpec,
    DreoFeatureSpec,
)

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=15)
MIN_RANGE_LEN = 2


def _set_toggle_switches_to_state(
    device_data: Any,
    state: dict[str, Any],
    model_config: dict[str, Any],
) -> None:
    """Set toggle switch fields on data object from state."""
    toggle_switches = get_conf_section(
        model_config, DreoEntityConfigSpec.TOGGLE_ENTITY_CONF
    )
    for toggle_switch in toggle_switches.values():
        field = toggle_switch.get("field")
        operable_when_off = toggle_switch.get("operableWhenOff", False)
        if (val := state.get(field)) is not None:
            setattr(device_data, field, bool(val))
        if not operable_when_off and not device_data.is_on:
            setattr(device_data, field, False)


def get_conf_section(
    model_config: dict[str, Any], section: DreoEntityConfigSpec
) -> dict[str, Any]:
    """Safely fetch a config section as a dict (empty if missing)."""
    value = model_config.get(section)
    return value if isinstance(value, dict) else {}


def get_conf(
    model_config: dict[str, Any],
    section: DreoEntityConfigSpec,
    key: DreoFeatureSpec,
    default: Any | None = None,
) -> Any:
    """Safely fetch a nested config value with a default."""
    return get_conf_section(model_config, section).get(key, default)


class DreoGenericDeviceData:
    """Base data for all Dreo devices."""

    available: bool = False
    is_on: bool = False

    def __init__(self, *, available: bool = False, is_on: bool = False) -> None:
        """Initialize generic device data."""
        self.available = available
        self.is_on = is_on


class DreoFanDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo fan devices."""

    mode: str | None = None
    oscillate: bool | None = None
    speed_percentage: int | None = None
    model_config: dict[str, Any] | None = None
    fixed_angle: dict[str, Any] | None = None
    oscrange: dict[str, Any] | None = None
    hfixedangle: dict[str, Any] | None = None
    vfixedangle: dict[str, Any] | None = None
    hoscrange: dict[str, Any] | None = None
    voscrange: dict[str, Any] | None = None
    hfixed_angle_range: str | None = None
    vfixed_angle_range: str | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        oscillate: bool | None = None,
        speed_percentage: int | None = None,
        light_mode: str | None = None,
        display_mode: str | None = None,
        model_config: dict[str, Any] | None = None,
        fixed_angle: dict[str, Any] | None = None,
        oscrange: dict[str, Any] | None = None,
        hfixedangle: dict[str, Any] | None = None,
        vfixedangle: dict[str, Any] | None = None,
        hoscrange: dict[str, Any] | None = None,
        voscrange: dict[str, Any] | None = None,
        hfixed_angle_range: str | None = None,
        vfixed_angle_range: str | None = None,
    ) -> None:
        """Initialize fan device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.oscillate = oscillate
        self.speed_percentage = speed_percentage
        self.light_mode = light_mode
        self.display_mode = display_mode
        self.model_config = model_config
        self.fixed_angle = fixed_angle
        self.oscrange = oscrange
        self.hfixedangle = hfixedangle
        self.vfixedangle = vfixedangle
        self.hoscrange = hoscrange
        self.voscrange = voscrange
        self.hfixed_angle_range = hfixed_angle_range
        self.vfixed_angle_range = vfixed_angle_range

    @staticmethod
    def process_fan_data(  # noqa: PLR0912
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoFanDeviceData:
        """Process fan device specific data."""
        fan_data = DreoFanDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            fan_data.mode = str(mode)

        if (oscillate := state.get(DreoDirective.OSCILLATE)) is not None:
            fan_data.oscillate = bool(oscillate)

        if (speed := state.get(DreoDirective.SPEED)) is not None:
            speed_range = get_conf(
                model_config,
                DreoEntityConfigSpec.FAN_ENTITY_CONF,
                DreoFeatureSpec.SPEED_RANGE,
            )
            if speed_range and len(speed_range) >= MIN_RANGE_LEN:
                fan_data.speed_percentage = int(
                    ranged_value_to_percentage(tuple(speed_range), float(speed))
                )

        if (lm := state.get(DreoDirective.LIGHTMODE)) is not None:
            fan_data.light_mode = str(lm) if not isinstance(lm, str) else lm

        if (dm := state.get(DreoDirective.DISPLAY_MODE)) is not None:
            fan_data.display_mode = str(dm) if not isinstance(dm, str) else dm

        if (fixed_angle := state.get(DreoDirective.FIXED_ANGLE)) is not None:
            fan_data.fixed_angle = fixed_angle

        if (oscrange := state.get(DreoDirective.OSCRANGE)) is not None:
            fan_data.oscrange = oscrange

        if (hfixedangle := state.get(DreoDirective.HFIXEDANGLE)) is not None:
            fan_data.hfixedangle = hfixedangle

        if (vfixedangle := state.get(DreoDirective.VFIXEDANGLE)) is not None:
            fan_data.vfixedangle = vfixedangle

        if (hoscrange := state.get(DreoDirective.HOSCRANGE)) is not None:
            fan_data.hoscrange = hoscrange

        if (voscrange := state.get(DreoDirective.VOSCRANGE)) is not None:
            fan_data.voscrange = voscrange

        if (
            hfixed_angle_range := state.get(DreoDirective.HFIXED_ANGLE_RANGE)
        ) is not None:
            fan_data.hfixed_angle_range = str(hfixed_angle_range)

        if (
            vfixed_angle_range := state.get(DreoDirective.VFIXED_ANGLE_RANGE)
        ) is not None:
            fan_data.vfixed_angle_range = str(vfixed_angle_range)

        _set_toggle_switches_to_state(fan_data, state, model_config)

        return fan_data


class DreoCirculationFanDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo circulation fan devices."""

    mode: str | None = None
    speed_level: int | None = None
    speed_percentage: int | None = None
    oscmode: str | None = None
    rgb_state: bool | None = None
    rgb_mode: str | None = None
    rgb_color: int | None = None
    rgb_brightness: int | None = None
    rgb_speed: str | None = None
    model_config: dict[str, Any] | None = None
    fixed_angle: dict[str, Any] | None = None
    oscrange: dict[str, Any] | None = None
    hfixedangle: dict[str, Any] | None = None
    vfixedangle: dict[str, Any] | None = None
    hoscrange: dict[str, Any] | None = None
    voscrange: dict[str, Any] | None = None
    hfixed_angle_range: str | None = None
    vfixed_angle_range: str | None = None
    hwfpangle: str | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        speed_level: int | None = None,
        speed_percentage: int | None = None,
        light_mode: str | None = None,
        oscmode: str | None = None,
        rgb_state: bool | None = None,
        rgb_mode: str | None = None,
        rgb_color: int | None = None,
        rgb_brightness: int | None = None,
        rgb_speed: str | None = None,
        model_config: dict[str, Any] | None = None,
        fixed_angle: dict[str, Any] | None = None,
        oscrange: dict[str, Any] | None = None,
        hfixedangle: dict[str, Any] | None = None,
        vfixedangle: dict[str, Any] | None = None,
        hoscrange: dict[str, Any] | None = None,
        voscrange: dict[str, Any] | None = None,
        hfixed_angle_range: str | None = None,
        vfixed_angle_range: str | None = None,
        hwfpangle: str | None = None,
    ) -> None:
        """Initialize circulation fan device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.speed_level = speed_level
        self.speed_percentage = speed_percentage
        self.light_mode = light_mode
        self.oscmode = oscmode
        self.rgb_state = rgb_state
        self.rgb_mode = rgb_mode
        self.rgb_color = rgb_color
        self.rgb_brightness = rgb_brightness
        self.rgb_speed = rgb_speed
        self.model_config = model_config
        self.fixed_angle = fixed_angle
        self.oscrange = oscrange
        self.hfixedangle = hfixedangle
        self.vfixedangle = vfixedangle
        self.hoscrange = hoscrange
        self.voscrange = voscrange
        self.hfixed_angle_range = hfixed_angle_range
        self.vfixed_angle_range = vfixed_angle_range
        self.hwfpangle = hwfpangle

    @staticmethod
    def process_circulation_fan_data(  # noqa: PLR0912
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoCirculationFanDeviceData:
        """Process circulation fan device specific data."""
        fan_data = DreoCirculationFanDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            fan_data.mode = str(mode)

        if (speed := state.get(DreoDirective.SPEED)) is not None:
            fan_data.speed_level = int(speed)
            speed_range = get_conf(
                model_config,
                DreoEntityConfigSpec.FAN_ENTITY_CONF,
                DreoFeatureSpec.SPEED_RANGE,
            )
            if speed_range and len(speed_range) >= MIN_RANGE_LEN:
                fan_data.speed_percentage = int(
                    ranged_value_to_percentage(tuple(speed_range), float(speed))
                )

        if (osc_mode := state.get(DreoDirective.OSCMODE)) is not None:
            fan_data.oscmode = osc_mode

        if (rgb_switch := state.get(DreoDirective.AMBIENT_SWITCH)) is not None:
            fan_data.rgb_state = bool(rgb_switch)

        if (rgb_mode := state.get(DreoDirective.AMBIENT_RGB_MODE)) is not None:
            fan_data.rgb_mode = str(rgb_mode)

        if (rgb_color := state.get(DreoDirective.AMBIENT_RGB_COLOR)) is not None:
            fan_data.rgb_color = int(rgb_color)

        if (
            rgb_brightness := state.get(DreoDirective.AMBIENT_RGB_BRIGHTNESS)
        ) is not None:
            fan_data.rgb_brightness = int(rgb_brightness)

        if (rgb_speed := state.get(DreoDirective.AMBIENT_RGB_SPEED)) is not None:
            fan_data.rgb_speed = str(rgb_speed)

        if (light_mode := state.get(DreoDirective.LIGHTMODE)) is not None:
            fan_data.light_mode = (
                str(light_mode) if not isinstance(light_mode, str) else light_mode
            )

        if (fixed_angle := state.get(DreoDirective.FIXED_ANGLE)) is not None:
            fan_data.fixed_angle = fixed_angle

        if (oscrange := state.get(DreoDirective.OSCRANGE)) is not None:
            fan_data.oscrange = oscrange

        if (hfixedangle := state.get(DreoDirective.HFIXEDANGLE)) is not None:
            fan_data.hfixedangle = hfixedangle

        if (vfixedangle := state.get(DreoDirective.VFIXEDANGLE)) is not None:
            fan_data.vfixedangle = vfixedangle

        if (hoscrange := state.get(DreoDirective.HOSCRANGE)) is not None:
            fan_data.hoscrange = hoscrange

        if (voscrange := state.get(DreoDirective.VOSCRANGE)) is not None:
            fan_data.voscrange = voscrange

        if (
            hfixed_angle_range := state.get(DreoDirective.HFIXED_ANGLE_RANGE)
        ) is not None:
            fan_data.hfixed_angle_range = str(hfixed_angle_range)

        if (
            vfixed_angle_range := state.get(DreoDirective.VFIXED_ANGLE_RANGE)
        ) is not None:
            fan_data.vfixed_angle_range = str(vfixed_angle_range)

        if (hwfpangle := state.get(DreoDirective.HWFPANGLE)) is not None:
            fan_data.hwfpangle = str(hwfpangle)

        _set_toggle_switches_to_state(fan_data, state, model_config)

        return fan_data


class DreoHacDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo HAC (Air Conditioner) devices."""

    mode: str | None = None
    hvac_mode: str | None = None
    speed_level: int | None = None
    speed_percentage: int | None = None
    oscillate: bool | None = None
    current_temperature: float | None = None
    target_temperature: float | None = None
    target_humidity: float | None = None
    model_config: dict[str, Any] | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        hvac_mode: str | None = None,
        speed_level: int | None = None,
        speed_percentage: int | None = None,
        oscillate: bool | None = None,
        target_temperature: float | None = None,
        target_humidity: float | None = None,
        model_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize HAC device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.hvac_mode = hvac_mode
        self.speed_level = speed_level
        self.speed_percentage = speed_percentage
        self.oscillate = oscillate
        self.target_temperature = target_temperature
        self.target_humidity = target_humidity
        self.model_config = model_config

    @staticmethod
    def process_hac_data(
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoHacDeviceData:
        """Process HAC device specific data."""
        hac_data = DreoHacDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (hvac_mode := state.get(DreoDirective.HVAC_MODE)) is not None:
            hac_data.hvac_mode = str(hvac_mode)

        if (mode := state.get(DreoDirective.MODE)) is not None:
            hac_data.mode = str(mode)
            if mode in ["sleep", "eco"]:
                hac_data.hvac_mode = HVACMode.COOL

        if (speed := state.get(DreoDirective.SPEED)) is not None:
            hac_data.speed_level = int(speed)
            speed_range = get_conf(
                model_config,
                DreoEntityConfigSpec.FAN_ENTITY_CONF,
                DreoFeatureSpec.SPEED_RANGE,
            )
            if speed_range and len(speed_range) >= MIN_RANGE_LEN:
                hac_data.speed_percentage = int(
                    ranged_value_to_percentage(tuple(speed_range), float(speed))
                )

        if (temp := state.get(DreoDirective.TEMPERATURE)) is not None:
            hac_data.target_temperature = float(temp)

        if (humidity := state.get(DreoDirective.HUMIDITY)) is not None:
            hac_data.target_humidity = float(humidity)

        if (osc := state.get(DreoDirective.SWING_SWITCH)) is not None:
            hac_data.oscillate = bool(osc)

        _set_toggle_switches_to_state(hac_data, state, model_config)

        return hac_data


class DreoHeaterDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo Heater devices."""

    hvac_mode: str | None = None
    mode: str | None = None
    target_temperature: float | None = None
    current_temperature: float | None = None
    heat_level: str | None = None
    oscillate: bool | None = None
    dispmode: bool | None = None
    light_mode: str | None = None
    oscangle: str | None = None
    oscmode: str | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        hvac_mode: str | None = None,
        mode: str | None = None,
        target_temperature: float | None = None,
        current_temperature: float | None = None,
        heat_level: str | None = None,
        oscillate: bool | None = None,
        dispmode: bool | None = None,
        light_mode: str | None = None,
        oscangle: str | None = None,
        oscmode: str | None = None,
    ) -> None:
        """Initialize Heater device data."""
        super().__init__(available=available, is_on=is_on)
        self.hvac_mode = hvac_mode
        self.mode = mode
        self.target_temperature = target_temperature
        self.current_temperature = current_temperature
        self.heat_level = heat_level
        self.oscillate = oscillate
        self.dispmode = dispmode
        self.display_mode = light_mode
        self.oscangle = oscangle
        self.oscmode = oscmode

    @staticmethod
    def process_heater_data(
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoHeaterDeviceData:
        """Process heater device specific data."""
        heater_data = DreoHeaterDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
        )

        if hvac_mode := state.get(DreoDirective.HVAC_MODE):
            heater_data.hvac_mode = str(hvac_mode)

        if mode := state.get(DreoDirective.MODE):
            heater_data.mode = str(mode)

        if temp := state.get(DreoDirective.TEMPERATURE):
            heater_data.current_temperature = float(temp)

        if target_temp := state.get(DreoDirective.ECOLEVEL):
            heater_data.target_temperature = float(target_temp)

        if heat_level := state.get(DreoDirective.HEAT_LEVEL):
            heater_data.heat_level = str(heat_level)

        if oscillate := state.get(DreoDirective.OSCILLATE):
            heater_data.oscillate = bool(oscillate)

        if dispmode := state.get(DreoDirective.DISPLAY_MODE):
            heater_data.dispmode = bool(dispmode)

        if light_mode := state.get(DreoDirective.LIGHTMODE):
            heater_data.light_mode = str(light_mode)

        if oscangle := state.get(DreoDirective.OSCANGLE):
            heater_data.oscangle = str(oscangle)

        if oscmode := state.get(DreoDirective.OSCMODE):
            heater_data.oscmode = str(oscmode)

        _set_toggle_switches_to_state(heater_data, state, model_config)

        return heater_data


class DreoHecDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo HEC (Hybrid Evaporative Cooler) devices."""

    mode: str | None = None
    speed_level: int | None = None
    speed_percentage: int | None = None
    oscillate: bool | None = None
    target_humidity: float | None = None
    current_humidity: float | None = None
    current_temperature: float | None = None
    rgb_state: bool | None = None
    rgb_mode: str | None = None
    rgb_color: int | None = None
    rgb_brightness: int | None = None
    rgb_speed: str | None = None
    humidity_switch: bool | None = None
    humidity_mode: str | None = None
    foglevel: str | None = None
    model_config: dict[str, Any] | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        speed_level: int | None = None,
        speed_percentage: int | None = None,
        oscillate: bool | None = None,
        target_humidity: float | None = None,
        current_humidity: float | None = None,
        current_temperature: float | None = None,
        rgb_state: bool | None = None,
        rgb_mode: str | None = None,
        rgb_color: int | None = None,
        rgb_brightness: int | None = None,
        rgb_speed: str | None = None,
        humidity_switch: bool | None = None,
        humidity_mode: str | None = None,
        foglevel: str | None = None,
        model_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize HEC device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.speed_level = speed_level
        self.speed_percentage = speed_percentage
        self.oscillate = oscillate
        self.target_humidity = target_humidity
        self.current_humidity = current_humidity
        self.current_temperature = current_temperature
        self.rgb_state = rgb_state
        self.rgb_mode = rgb_mode
        self.rgb_color = rgb_color
        self.rgb_brightness = rgb_brightness
        self.rgb_speed = rgb_speed
        self.humidity_switch = humidity_switch
        self.humidity_mode = humidity_mode
        self.foglevel = foglevel
        self.model_config = model_config

    @staticmethod
    def process_hec_data(  # noqa: PLR0912
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoHecDeviceData:
        """Process HEC device specific data."""
        hec_data = DreoHecDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            hec_data.mode = str(mode)

        if (speed := state.get(DreoDirective.SPEED)) is not None:
            hec_data.speed_level = int(speed)
            speed_range = get_conf(
                model_config,
                DreoEntityConfigSpec.FAN_ENTITY_CONF,
                DreoFeatureSpec.SPEED_RANGE,
            )
            if speed_range and len(speed_range) >= MIN_RANGE_LEN:
                hec_data.speed_percentage = int(
                    ranged_value_to_percentage(tuple(speed_range), float(speed))
                )

        if (oscillate := state.get(DreoDirective.OSCILLATE)) is not None:
            hec_data.oscillate = bool(oscillate)

        if (humidity_switch := state.get(DreoDirective.HUMIDITY_SWITCH)) is not None:
            hec_data.humidity_switch = bool(humidity_switch)

        if (humidity_mode := state.get(DreoDirective.HUMIDITY_MODE)) is not None:
            hec_data.humidity_mode = str(humidity_mode)

        if (humidity := state.get(DreoDirective.HUMIDITY)) is not None:
            hec_data.target_humidity = float(humidity)

        if (humidity := state.get(DreoDirective.HUMIDITY_SENSOR)) is not None:
            hec_data.current_humidity = float(humidity)

        if (foglevel := state.get(DreoDirective.FOGLEVEL)) is not None:
            hec_data.foglevel = str(foglevel)

        if (temperature := state.get(DreoDirective.TEMPERATURE)) is not None:
            hec_data.current_temperature = float(temperature)

        if (rgb_switch := state.get(DreoDirective.AMBIENT_SWITCH)) is not None:
            hec_data.rgb_state = bool(rgb_switch)

        if (rgb_mode := state.get(DreoDirective.AMBIENT_RGB_MODE)) is not None:
            hec_data.rgb_mode = str(rgb_mode)

        if (rgb_color := state.get(DreoDirective.AMBIENT_RGB_COLOR)) is not None:
            hec_data.rgb_color = int(rgb_color)

        if (
            rgb_brightness := state.get(DreoDirective.AMBIENT_RGB_BRIGHTNESS)
        ) is not None:
            hec_data.rgb_brightness = int(rgb_brightness)

        if (rgb_speed := state.get(DreoDirective.AMBIENT_RGB_SPEED)) is not None:
            hec_data.rgb_speed = str(rgb_speed)

        _set_toggle_switches_to_state(hec_data, state, model_config)

        return hec_data


class DreoHapDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo HAP (Air Purifier) devices."""

    mode: str | None = None
    speed_level: int | None = None
    speed_percentage: int | None = None
    led_switch: bool | None = None
    lightsensor_switch: bool | None = None
    childlock_switch: bool | None = None
    mute_switch: bool | None = None
    display_mode: str | None = None
    model_config: dict[str, Any] | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        speed_level: int | None = None,
        speed_percentage: int | None = None,
        led_switch: bool | None = None,
        lightsensor_switch: bool | None = None,
        childlock_switch: bool | None = None,
        mute_switch: bool | None = None,
        display_mode: str | None = None,
        model_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize HAP device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.speed_level = speed_level
        self.speed_percentage = speed_percentage
        self.led_switch = led_switch
        self.lightsensor_switch = lightsensor_switch
        self.childlock_switch = childlock_switch
        self.mute_switch = mute_switch
        self.display_mode = display_mode
        self.model_config = model_config

    @staticmethod
    def process_hap_data(
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoHapDeviceData:
        """Process HAP device specific data."""
        hap_data = DreoHapDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            hap_data.mode = str(mode)

        if (display_mode := state.get(DreoDirective.DISPLAY_MODE)) is not None:
            hap_data.display_mode = str(display_mode)

        if (speed := state.get(DreoDirective.SPEED)) is not None:
            hap_data.speed_level = int(speed)
            speed_range = get_conf(
                model_config,
                DreoEntityConfigSpec.FAN_ENTITY_CONF,
                DreoFeatureSpec.SPEED_RANGE,
            )
            if speed_range and len(speed_range) >= MIN_RANGE_LEN:
                hap_data.speed_percentage = int(
                    ranged_value_to_percentage(tuple(speed_range), float(speed))
                )

        _set_toggle_switches_to_state(hap_data, state, model_config)

        return hap_data


class DreoDehumidifierDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo Dehumidifier devices (HDH)."""

    mode: str | None = None
    wind_level: str | None = None
    target_humidity: float | None = None
    current_humidity: float | None = None
    rgb_threshold: str | None = None
    filter_threshold: int | None = None
    work_time: int | None = None
    model_config: dict[str, Any] | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        wind_level: str | None = None,
        target_humidity: float | None = None,
        current_humidity: float | None = None,
        model_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize dehumidifier device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.wind_level = wind_level
        self.target_humidity = target_humidity
        self.current_humidity = current_humidity
        self.model_config = model_config

    @staticmethod
    def process_dehumidifier_data(
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoDehumidifierDeviceData:
        """Process dehumidifier device specific data."""
        hdh = DreoDehumidifierDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            hdh.mode = str(mode)

        if (wind := state.get("windlevel")) is not None:
            hdh.wind_level = str(wind)

        if (rh := state.get("rh_auto")) is not None:
            hdh.target_humidity = float(rh)

        if (humidity := state.get(DreoDirective.HUMIDITY_SENSOR)) is not None:
            hdh.current_humidity = float(humidity)

        if (flt := state.get("filter_threshold")) is not None:
            hdh.filter_threshold = int(flt)

        _set_toggle_switches_to_state(hdh, state, model_config)

        return hdh


class DreoHumidifierDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo Humidifier devices."""

    mode: str | None = None
    target_humidity: float | None = None
    current_humidity: float | None = None
    fog_level: int | None = None
    led_level: str | None = None
    rgb_level: str | None = None
    rgb_threshold: str | None = None
    filter_time: int | None = None
    work_time: int | None = None
    rgb_state: bool | None = None
    rgb_mode: str | None = None
    rgb_color: int | None = None
    rgb_brightness: int | None = None
    rgb_speed: str | None = None
    rgb_breath_speed: int | None = None
    rgb_cycle_speed: int | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        target_humidity: float | None = None,
        current_humidity: float | None = None,
        fog_level: int | None = None,
        led_level: str | None = None,
        rgb_level: str | None = None,
        rgb_threshold: str | None = None,
        filter_time: int | None = None,
        work_time: int | None = None,
        model_config: dict[str, Any] | None = None,
        rgb_state: bool | None = None,
        rgb_mode: str | None = None,
        rgb_color: int | None = None,
        rgb_brightness: int | None = None,
        rgb_speed: str | None = None,
        rgb_breath_speed: int | None = None,
        rgb_cycle_speed: int | None = None,
    ) -> None:
        """Initialize Dreo humidifier device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.target_humidity = target_humidity
        self.current_humidity = current_humidity
        self.fog_level = fog_level
        self.led_level = led_level
        self.rgb_level = rgb_level
        self.rgb_threshold = rgb_threshold
        self.filter_time = filter_time
        self.work_time = work_time
        self.model_config = model_config
        self.rgb_state = rgb_state
        self.rgb_mode = rgb_mode
        self.rgb_color = rgb_color
        self.rgb_brightness = rgb_brightness
        self.rgb_speed = rgb_speed
        self.rgb_breath_speed = rgb_breath_speed
        self.rgb_cycle_speed = rgb_cycle_speed

    @staticmethod
    def process_humidifier_data(  # noqa: PLR0912
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoHumidifierDeviceData:
        """Process humidifier device specific data."""
        humidifier_data = DreoHumidifierDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            humidifier_data.mode = str(mode)

        # Humidity ranges - different for different modes
        if (rh_auto := state.get("rh_auto")) is not None:
            humidifier_data.target_humidity = float(rh_auto)

        if (rh_sleep := state.get("rh_sleep")) is not None:
            humidifier_data.target_humidity = float(rh_sleep)

        if (humidity := state.get("humidity_sensor")) is not None:
            humidifier_data.current_humidity = float(humidity)

        if (fog_level := state.get("fog_level")) is not None:
            humidifier_data.fog_level = int(fog_level)

        if (led_level := state.get("ledlevel")) is not None:
            humidifier_data.led_level = str(led_level)

        if (rgb_level := state.get("rgblevel")) is not None:
            humidifier_data.rgb_level = str(rgb_level)

        if (rgb_threshold := state.get("rgb_threshold")) is not None:
            humidifier_data.rgb_threshold = str(rgb_threshold)

        if (filter_time := state.get("filter_time")) is not None:
            humidifier_data.filter_time = int(filter_time)

        if (work_time := state.get("work_time")) is not None:
            humidifier_data.work_time = int(work_time)

        if (rgb_state := state.get(DreoDirective.AMBIENT_SWITCH)) is not None:
            humidifier_data.rgb_state = bool(rgb_state)

        if (rgb_mode := state.get(DreoDirective.AMBIENT_RGB_MODE)) is not None:
            humidifier_data.rgb_mode = str(rgb_mode)

        if (rgb_color := state.get(DreoDirective.AMBIENT_RGB_COLOR)) is not None:
            humidifier_data.rgb_color = int(rgb_color)

        # Models like DR-HHM005S report the night-light state under different keys:
        # rgbmode ("Custom"/"Off"/...) and rgb_color (packed 24-bit int). Parse these
        # when present; they override the atm* values since this firmware never reports
        # the atm* keys.
        if (hum_rgb_mode := state.get(DreoDirective.HUMIDIFIER_RGB_MODE)) is not None:
            humidifier_data.rgb_mode = str(hum_rgb_mode)
            humidifier_data.rgb_state = str(hum_rgb_mode) != "Off"

        if (hum_rgb_color := state.get(DreoDirective.HUMIDIFIER_RGB_COLOR)) is not None:
            humidifier_data.rgb_color = int(hum_rgb_color)

        if (
            rgb_brightness := state.get(DreoDirective.AMBIENT_RGB_BRIGHTNESS)
        ) is not None:
            humidifier_data.rgb_brightness = int(rgb_brightness)

        if (rgb_speed := state.get(DreoDirective.AMBIENT_RGB_SPEED)) is not None:
            humidifier_data.rgb_speed = str(rgb_speed)

        if (rgb_breath_speed := state.get(DreoDirective.RGB_BREATH_SPEED)) is not None:
            humidifier_data.rgb_breath_speed = int(rgb_breath_speed)

        if (rgb_cycle_speed := state.get(DreoDirective.RGB_CYCLE_SPEED)) is not None:
            humidifier_data.rgb_cycle_speed = int(rgb_cycle_speed)

        _set_toggle_switches_to_state(humidifier_data, state, model_config)

        return humidifier_data


class DreoCeilingFanDeviceData(DreoGenericDeviceData):
    """Data specific to Dreo Ceiling Fan devices."""

    mode: str | None = None
    speed_level: int | None = None
    speed_percentage: int | None = None
    light_switch: bool | None = None
    brightness: int | None = None
    colortemp: int | None = None
    rgb_state: bool | None = None
    rgb_mode: str | None = None
    rgb_color: int | None = None
    rgb_brightness: int | None = None
    rgb_speed: str | None = None
    model_config: dict[str, Any] | None = None

    def __init__(  # noqa: PLR0913
        self,
        *,
        available: bool = False,
        is_on: bool = False,
        mode: str | None = None,
        speed_level: int | None = None,
        speed_percentage: int | None = None,
        light_switch: bool | None = None,
        brightness: int | None = None,
        colortemp: int | None = None,
        rgb_state: bool | None = None,
        rgb_mode: str | None = None,
        rgb_color: int | None = None,
        rgb_brightness: int | None = None,
        rgb_speed: str | None = None,
        model_config: dict[str, Any] | None = None,
    ) -> None:
        """Initialize ceiling fan device data."""
        super().__init__(available=available, is_on=is_on)
        self.mode = mode
        self.speed_level = speed_level
        self.speed_percentage = speed_percentage
        self.light_switch = light_switch
        self.brightness = brightness
        self.colortemp = colortemp
        self.rgb_state = rgb_state
        self.rgb_mode = rgb_mode
        self.rgb_color = rgb_color
        self.rgb_brightness = rgb_brightness
        self.rgb_speed = rgb_speed
        self.model_config = model_config

    @staticmethod
    def process_ceiling_fan_data(
        state: dict[str, Any], model_config: dict[str, Any]
    ) -> DreoCeilingFanDeviceData:
        """Process ceiling fan device specific data."""
        ceiling_fan_data = DreoCeilingFanDeviceData(
            available=state.get(DreoDirective.CONNECTED, False),
            is_on=state.get(DreoDirective.POWER_SWITCH, False),
            model_config=model_config,
        )

        if (mode := state.get(DreoDirective.MODE)) is not None:
            ceiling_fan_data.mode = str(mode)

        if (speed := state.get(DreoDirective.SPEED)) is not None:
            ceiling_fan_data.speed_level = int(speed)
            speed_range = get_conf(
                model_config,
                DreoEntityConfigSpec.FAN_ENTITY_CONF,
                DreoFeatureSpec.SPEED_RANGE,
            )
            if speed_range and len(speed_range) >= MIN_RANGE_LEN:
                ceiling_fan_data.speed_percentage = int(
                    ranged_value_to_percentage(tuple(speed_range), float(speed))
                )

        if (light_switch := state.get(DreoDirective.LIGHT_SWITCH)) is not None:
            ceiling_fan_data.light_switch = bool(light_switch)

        if (brightness := state.get(DreoDirective.LIGHT_BRIGHTNESS)) is not None:
            ceiling_fan_data.brightness = int(brightness)

        if (color_temp := state.get(DreoDirective.LIGHT_COLOR_TEMP)) is not None:
            ceiling_fan_data.colortemp = int(color_temp)

        if (rgb_switch := state.get(DreoDirective.AMBIENT_SWITCH)) is not None:
            ceiling_fan_data.rgb_state = bool(rgb_switch)

        if (rgb_mode := state.get(DreoDirective.AMBIENT_RGB_MODE)) is not None:
            ceiling_fan_data.rgb_mode = str(rgb_mode)

        if (rgb_color := state.get(DreoDirective.AMBIENT_RGB_COLOR)) is not None:
            ceiling_fan_data.rgb_color = int(rgb_color)

        if (
            rgb_brightness := state.get(DreoDirective.AMBIENT_RGB_BRIGHTNESS)
        ) is not None:
            ceiling_fan_data.rgb_brightness = int(rgb_brightness)

        if (rgb_speed := state.get(DreoDirective.AMBIENT_RGB_SPEED)) is not None:
            ceiling_fan_data.rgb_speed = str(rgb_speed)

        _set_toggle_switches_to_state(ceiling_fan_data, state, model_config)

        return ceiling_fan_data


DreoDeviceData = (
    DreoFanDeviceData
    | DreoCirculationFanDeviceData
    | DreoHacDeviceData
    | DreoHeaterDeviceData
    | DreoHecDeviceData
    | DreoHapDeviceData
    | DreoHumidifierDeviceData
    | DreoDehumidifierDeviceData
    | DreoCeilingFanDeviceData
)


class DreoDataUpdateCoordinator(DataUpdateCoordinator[DreoDeviceData | None]):
    """Class to manage fetching Dreo data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DreoClient,
        device_id: str,
        device_type: str,
        model_config: dict[str, Any],
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client
        self.device_id = device_id
        self.device_type = device_type
        self.model_config = model_config
        self.data_processor: (
            Callable[[dict[str, Any], dict[str, Any]], DreoDeviceData] | None
        )

        if self.device_type == DreoDeviceType.FAN:
            self.data_processor = DreoFanDeviceData.process_fan_data
        elif self.device_type == DreoDeviceType.CIR_FAN:
            self.data_processor = (
                DreoCirculationFanDeviceData.process_circulation_fan_data
            )
        elif self.device_type in [
            DreoDeviceType.CEILING_FAN,
            DreoDeviceType.RGBLIGHT_CEILING_FAN,
        ]:
            self.data_processor = DreoCeilingFanDeviceData.process_ceiling_fan_data
        elif self.device_type == DreoDeviceType.HAC:
            self.data_processor = DreoHacDeviceData.process_hac_data
        elif self.device_type == DreoDeviceType.HEATER:
            self.data_processor = DreoHeaterDeviceData.process_heater_data
        elif self.device_type == DreoDeviceType.HEC:
            self.data_processor = DreoHecDeviceData.process_hec_data
        elif self.device_type == DreoDeviceType.HAP:
            self.data_processor = DreoHapDeviceData.process_hap_data
        elif self.device_type == DreoDeviceType.HUMIDIFIER:
            self.data_processor = DreoHumidifierDeviceData.process_humidifier_data
        elif self.device_type == DreoDeviceType.DEHUMIDIFIER:
            self.data_processor = DreoDehumidifierDeviceData.process_dehumidifier_data
        else:
            _LOGGER.warning(
                "Unsupported device type: %s for model: %s - "
                "data will not be processed",
                self.device_type,
                self.device_id,
            )
            self.data_processor = None

    async def _async_update_data(self) -> DreoDeviceData | None:
        """Get device status from Dreo API and process it."""

        def _raise_no_status() -> NoReturn:
            """Raise UpdateFailed for no status available."""
            message = (
                "No status available for device "
                f"{self.device_id} with type {self.device_type}"
            )
            raise UpdateFailed(message)

        def _raise_no_processor() -> NoReturn:
            """Raise UpdateFailed for no data processor available."""
            message = (
                "No data processor available for device "
                f"{self.device_id} with type {self.device_type}"
            )
            raise UpdateFailed(message)

        try:
            state = await self.hass.async_add_executor_job(
                self.client.get_status, self.device_id
            )

            if state is None:
                _raise_no_status()

            if self.data_processor is None:
                _raise_no_processor()

            return self.data_processor(state, self.model_config)
        except DreoException as error:
            message = f"Error communicating with Dreo API: {error}"
            raise UpdateFailed(message) from error
        except Exception as error:
            message = f"Unexpected error: {error}"
            raise UpdateFailed(message) from error
