"""
Select platform for wemportal component
"""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import _LOGGER, DOMAIN


async def async_setup_platform(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    """Setup the Wem Portal select."""

    coordinator = hass.data[DOMAIN]["coordinator"]

    entities: list[WemPortalSelect] = []
    for unique_id, values in coordinator.data.items():
        if values["platform"] == "select":
            entities.append(WemPortalSelect(coordinator, unique_id, values))

    async_add_entities(entities)


class WemPortalSelect(CoordinatorEntity, SelectEntity):
    """Representation of a WEM Portal Sensor."""

    def __init__(self, coordinator, _unique_id, entity_data):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._last_updated = None
        self._name = _unique_id
        self._parameter_id = entity_data["ParameterID"]
        self._unique_id = _unique_id
        self._icon = entity_data["icon"]
        self._options = entity_data["options"]
        self._options_names = entity_data["optionsNames"]
        self._module_index = entity_data["ModuleIndex"]
        self._module_type = entity_data["ModuleType"]

    async def async_select_option(self, option: str) -> None:
        """Call the API to change the parameter value"""
        await self.hass.async_add_executor_job(
            self.coordinator.api.change_value,
            self._parameter_id,
            self._module_index,
            self._module_type,
            self._options[self._options_names.index(option)],
        )

        self.coordinator.data[self._unique_id]["value"] = self._options[
            self._options_names.index(option)
        ]

        self.async_write_ha_state()

    @property
    def options(self) -> list[str]:
        """Return list of available options."""
        return self._options_names

    @property
    def current_option(self) -> str:
        """Return the current option."""
        return self._options_names[
            self._options.index(self.coordinator.data[self._unique_id]["value"])
        ]

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """When entity will be removed from hass."""
        self.coordinator.async_remove_listener(self.async_write_ha_state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of the binary sensor."""
        return self._unique_id

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        if self._last_updated is not None:
            attr["Last Updated"] = self._last_updated
        return attr

    async def async_update(self):
        """Update Entity
        Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()
