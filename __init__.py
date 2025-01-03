async def async_setup(hass, config):
    """Set up the garbage collection integration from YAML."""
    return True

async def async_setup_entry(hass, entry):
    """Set up garbage collection from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "garbage_collection")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "garbage_collection")
    return True
