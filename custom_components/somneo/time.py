"""Time entities for Somneo."""

from datetime import time
from typing import Any

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SomneoEntity


class ConfigEntryUniqueIdRequiredError(ValueError):
    """Raised when a config entry unique_id is missing."""

    def __init__(self) -> None:
        """Initialize exception."""
        super().__init__("Config entry unique_id is required")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Somneo from config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    if unique_id is None:
        raise ConfigEntryUniqueIdRequiredError
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data["dev_info"]

    # Add hour & min number_entity for each alarm.
    alarms = [
        SomneoTime(coordinator, unique_id, name, device_info, alarm)
        for alarm in coordinator.data["alarms"]
    ]

    async_add_entities(alarms, update_before_add=True)


class SomneoTime(SomneoEntity, TimeEntity):
    """Representation of a alarm time."""

    _attr_should_poll = True
    _attr_assumed_state = False
    _attr_available = True
    _attr_has_entity_name = True
    _attr_native_value = None
    _attr_translation_key = "time"

    def __init__(
        self,
        coordinator: Any,
        unique_id: str,
        name: str,
        dev_info: dict[str, Any],
        alarm: Any,
    ) -> None:
        """Initialize number entities."""
        super().__init__(
            coordinator, unique_id, name, dev_info, "alarm" + str(alarm) + "_time"
        )

        self._attr_translation_placeholders = {"number": str(alarm)}

        self._alarm = alarm

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["alarms"][self._alarm]["time"]

        self.async_write_ha_state()

    async def async_set_value(self, value: time) -> None:
        """Adjust Hours and Minutes."""
        await self.coordinator.async_set_alarm(self._alarm, alarm_time=value)
