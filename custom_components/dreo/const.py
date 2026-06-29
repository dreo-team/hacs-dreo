"""Constants for the Dreo integration."""

from enum import StrEnum

DOMAIN = "dreo"

# Cloud polling interval (seconds). The Dreo cloud API is rate limited, so the
# default is intentionally conservative; it can be tuned via the options flow.
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 3600


class DreoEntityConfigSpec(StrEnum):
    """Dreo config keys."""

    ENTITY_SUPPORTS = "entitySupports"
    TOP_CONFIG = "config"
    FAN_ENTITY_CONF = "fan_entity_config"
    LIGHT_ENTITY_CONF = "light_entity_config"
    RGBLIGHT_ENTITY_CONF = "rgbLight_entity_config"
    TOGGLE_ENTITY_CONF = "toggle_entity_config"
    SELECT_ENTITY_CONF = "select_entity_config"
    HUMIDIFIER_ENTITY_CONF = "humidifier_entity_config"
    NUMBER_ENTITY_CONF = "number_entity_config"
    SENSOR_ENTITY_CONF = "sensor_entity_config"
    HEATER_ENTITY_CONF = "heater_entity_config"


class DreoFeatureSpec(StrEnum):
    """Dreo value range keys."""

    PRESET_MODES = "preset_modes"
    HVAC_MODES = "hvac_modes"
    SPEED_RANGE = "speed_range"
    TEMPERATURE_RANGE = "temperature_range"
    HUMIDITY_RANGE = "humidity_range"
    BRIGHTNESS_PERCENTAGE = "brightness_percentage"
    RGB_BRIGHTNESS = "rgb_brightness"
    LIGHT_MODES = "light_modes"
    COLOR_TEMPERATURE_RANGE = "color_temperature_range"
    HUMIDIFIER_MODE_CONFIG = "humidity_mode_config"
    DIRECTIVE_GRAPH = "directive_graph"
    DESCRIPTION_LIMITS = "description_limits"
    AMBIENT_THRESHOLD = "ambient_threshold"
    SLIDE_COMPONENT = "slide_component"
    STATE_ATTR_NAME = "state_attr_name"
    DIRECTIVE_NAME = "directive_name"
    DIRECTIVE_VALUE = "directive_value"
    HVAC_MODE_VALUE = "hvac_mode_value"
    ATTR_NAME = "attr_name"
    ATTR_ICON = "attr_icon"
    THRESHOLD_RANGE = "threshold_range"
    DATA_RANGE = "data_range"
    STATUS_AVAILABLE_DEPENDENCIES = "status_available_dependencies"
    AMBIENT_STATUS_AVAILABLE_DEPENDENCIES = "ambient_status_available_dependencies"
    SENSOR_CLASS = "sensor_class"
    HVAC_MODE_RELATE_MAP = "hvac_mode_relate_map"
    HVAC_MODE_REPORT = "report"
    PRESET_MODE_CONTROL = "controls"
    SUPPORTED_FEATURES = "supported_features"
    FIXED_ANGLE = "fixed_angle"
    OSCRANGE = "oscrange"
    SENSOR_UNIT = "sensor_unit"


class DreoDirective(StrEnum):
    """Dreo directive keys."""

    CONNECTED = "connected"
    POWER_SWITCH = "power_switch"
    AMBIENT_SWITCH = "ambient_switch"
    AMBIENT_LIGHT_SWITCH = "ambient_light_switch"
    LIGHT_SWITCH = "light_switch"
    HUMIDITY_SWITCH = "humidity_switch"
    SWING_SWITCH = "swing_switch"
    MODE = "mode"
    OSCILLATE = "oscillate"
    OSCMODE = "oscmode"
    SPEED = "speed"
    LIGHTMODE = "lightmode"
    DISPLAY_MODE = "dispmode"
    HVAC_MODE = "hvacmode"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    AMBIENT_RGB_MODE = "atmmode"
    AMBIENT_RGB_COLOR = "atmcolor"
    AMBIENT_RGB_BRIGHTNESS = "atmbri"
    AMBIENT_RGB_SPEED = "atmspeed"
    LIGHT_BRIGHTNESS = "brightness"
    LIGHT_COLOR_TEMP = "colortemp"
    RGB_HUMIDITY_THRESHOLD = "rgb_threshold"
    HUMIDITY_SENSOR = "humidity_sensor"
    ECOLEVEL = "ecolevel"
    HEAT_LEVEL = "htalevel"
    OSCANGLE = "oscangle"
    HUMIDITY_MODE = "humidity_mode"
    FOGLEVEL = "foglevel"
    MAIN_SWITCH = "main_switch"
    FIXED_ANGLE = "fixed_angle"
    OSCRANGE = "oscrange"
    HFIXEDANGLE = "hfixedangle"
    VFIXEDANGLE = "vfixedangle"
    HOSCRANGE = "hoscrange"
    VOSCRANGE = "voscrange"
    HFIXED_ANGLE_RANGE = "hfixed_angle_range"
    VFIXED_ANGLE_RANGE = "vfixed_angle_range"
    HWFPANGLE = "hwfpangle"
    RGB_BREATH_SPEED = "rgb_breath_speed"
    RGB_CYCLE_SPEED = "rgb_cycle_speed"
    TEMP_UNITS = "temp_units"


class DreoDeviceType(StrEnum):
    """Dreo device types."""

    FAN = "fan"
    CIR_FAN = "circulation_fan"
    CEILING_FAN = "ceiling_fan"
    RGBLIGHT_CEILING_FAN = "rgblight_ceiling_fan"
    HAC = "hac"
    HEC = "hec"  # Hybrid Evaporative Cooler
    HAP = "hap"  # Air Purifier
    HUMIDIFIER = "humidifier"  # Humidifier
    DEHUMIDIFIER = "dehumidifier"  # Dehumidifier
    HEATER = "heater"


CIR_FAN_SWING_ENTITY = "swing_direction"


class DreoErrorCode(StrEnum):
    """Error translation keys used across the integration."""

    TURN_ON_FAILED = "turn_on_failed"
    TURN_OFF_FAILED = "turn_off_failed"
    SET_PRESET_MODE_FAILED = "set_preset_mode_failed"
    SET_SPEED_FAILED = "set_speed_failed"
    SET_FAN_MODE_FAILED = "set_fan_mode_failed"
    SET_SWING_FAILED = "set_swing_failed"
    SET_SWING_DIRECTION_FAILED = "set_swing_direction_failed"
    SET_BRIGHTNESS_FAILED = "set_brightness_failed"
    SET_TEMPERATURE_FAILED = "set_temperature_failed"
    SET_HUMIDITY_FAILED = "set_humidity_failed"
    SET_HEC_HUMIDITY_FAILED = "set_hec_humidity_failed"
    SET_HUMIDIFIER_MODE_FAILED = "set_humidifier_mode_failed"
    SET_HVAC_MODE_FAILED = "set_hvac_mode_failed"
    SET_RGB_SPEED_FAILED = "set_rgb_speed_failed"
    SET_FOLLOW_MODE_FAILED = "set_follow_mode_failed"
    SET_LED_SWITCH_FAILED = "set_led_switch_failed"
    SET_LIGHTSENSOR_SWITCH_FAILED = "set_lightsensor_switch_failed"
    SET_MUTE_SWITCH_FAILED = "set_mute_switch_failed"
    SET_HUMIDIFIER_HUMIDITY_FAILED = "set_humidifier_humidity_failed"
    HUMIDITY_NOT_SUPPORTED_IN_MODE = "humidity_not_supported_in_mode"
    SET_RGB_THRESHOLD_FAILED = "set_rgb_threshold_failed"
    SET_FIXED_ANGLE_FAILED = "set_fixed_angle_failed"
