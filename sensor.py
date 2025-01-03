import logging
import traceback
from datetime import timedelta
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv

from .ecowerf_api_client import GarbageCollectorAPI, EcowerfTokenError

logger = logging.getLogger(__name__)

DEFAULT_NAME = "Ecowerf Garbage Collection"
SCAN_INTERVAL = timedelta(hours=8)

SCHEDULE_URL = 'schedule_url'
CONSUMER = 'consumer'
PLATFORM = 'platform'

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(PLATFORM): cv.string,
    vol.Required(SCHEDULE_URL): cv.string,
    vol.Required(CONSUMER): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    logger.debug("setup_platform called")
    api_key = config.get(CONF_API_KEY)
    name = config.get(CONF_NAME)
    schedule_url = config.get(SCHEDULE_URL)
    consumer = config.get(CONSUMER)
    api = GarbageCollectorAPI(
        garbage_token_url='https://api.fostplus.be/recycle-public/app/v1/access-token',
        garbage_consumer=consumer,
        garbage_secret=api_key,
        garbage_schedule_url=schedule_url,
    )

    logger.debug(f"Adding entities for {api}, {name}")
    add_entities([GarbageCollectionSensor(api, name)], True)


class GarbageCollectionSensor(SensorEntity):
    def __init__(self, api, name):
        logger.debug(f"Sensor created with {name}")
        self._api = api
        self._name = name
        self._state = None
        self._schedule = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "schedule": self._schedule
        }

    def update(self):
        logger.debug("update called")

        try:
            data = self._api.get_schedule()
        except EcowerfTokenError:
            logger.error(f"Error getting a token from API")
            self._state = f"Please update the Ecowerf Garbage Collection API key"
            return
        except Exception as e:
            logger.error(f"Error fetching data from API: {e}")
            logger.error(traceback.format_exc())
            self._state = f"Can't fetch the garbage collection schedule"
            return

        logger.debug(f"Received data: {data}")

        if len(data) == 0:
            self._state = 'No garbage collection'
            return

        try:
            dt = data[0]['date']
            types = []

            for entry in data:
                if entry['date'] == dt:
                    types.append(entry['type'])

            self._state = f'{data[0]["dt_format"]}: {", ".join(types)}'
            self._schedule = data
            logger.debug(f"Sensor state set to {self._state}")
        except Exception as e:
            logger.error(f"Error parsing data `{data}` from API: {e}")
            self._state = f'Error parsing data `{data}` from API: {e}'
