"""
Sensor for NBP - Narodowy Bank Polski integration

For more details about this platform, please refer to the documentation at
https://github.com/korasinski/ha-nbp
"""
from datetime import datetime, timedelta
import json
import logging
import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_CODE, CONF_CURRENCY, CONF_NAME, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from .const import API_URL, CURRENCIES, DEFAULT_NAME, ICONS

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=60)

CURRENCY_SCHEMA = vol.Schema(
    {vol.Required(CONF_CODE): vol.In(CURRENCIES), vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
        vol.Required(CONF_CURRENCY): vol.All(cv.ensure_list, [CURRENCY_SCHEMA]),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the NBP sensors."""

    scan_interval = config.get(CONF_SCAN_INTERVAL)
    currencies = config.get(CONF_CURRENCY, [])
    min_scan_interval = timedelta(minutes=1)

    if not currencies:
        msg = "No currencies configured."
        hass.components.persistent_notification.create(msg, f"Sensor {DEFAULT_NAME}")
        _LOGGER.warning(msg)
        return

    if scan_interval < min_scan_interval:
        msg = f"Scan interval must be at least 1 minute (i.e. 00:00:01) - Configured Value: {scan_interval}. Configuration will use the default scan interval and continue."
        hass.components.persistent_notification.create(msg, f"Sensor {DEFAULT_NAME}")
        _LOGGER.warning(msg)
        scan_interval = DEFAULT_SCAN_INTERVAL

    _LOGGER.debug(f"{DEFAULT_NAME}: Scan Interval: {scan_interval}")

    updater = NBPUpdater(scan_interval)
    updater.update()
    if updater is None:
        if updater.data is None:
            msg = "Unhandled Error"
            hass.components.persistent_notification.create(
                f"{msg}. Please investigate logs.", f"Sensor {DEFAULT_NAME}"
            )
            raise Exception(
                f"{DEFAULT_NAME}: Invalid configuration for {DEFAULT_NAME} platform. Error Message: {msg}"
            )

    entity = []
    for currency in currencies:
        entity.append(NBPSensor(currency, updater))

    add_entities(entity, True)


class NBPSensor(Entity):
    """Representation of a NBP - Narodowy Bank Polski sensor."""

    def __init__(self, currency, updater):
        """Initialize the sensor."""
        self._updater = updater
        self._conversion = currency
        self._currency_code = currency[CONF_CODE]
        self._currency_name = None
        if CONF_NAME in currency:
            self._name = f"{currency.get(CONF_NAME)}"
        else:
            self._name = f"nbp_{self._currency_code}"
        self._unique_id = f"nbp_{self._currency_code}"
        self._icon = ICONS.get(self._currency_code, "USD")
        self._unit_of_measurement = "PLN"
        self._trading_date = datetime(1900, 1, 1)
        self._effective_date = datetime(1900, 1, 1)
        self._ask = None
        self._bid = None
        self._table_name = None
        self._table_no = None

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._updater.data is not None:
            self._table_name = self._updater.data["table"]
            self._table_no = self._updater.data["no"]
            self._effective_date = datetime.strptime(
                self._updater.data["effectiveDate"], "%Y-%m-%d"
            )
            self._trading_date = datetime.strptime(
                self._updater.data["tradingDate"], "%Y-%m-%d"
            )
            for currency in self._updater.data["rates"]:
                if currency["code"] == self._currency_code:
                    self._ask = currency["ask"]
                    self._bid = currency["bid"]
                    self._currency_name = currency["currency"]
                    self._currency_code = currency["code"]
        return self._ask

    @property
    def extra_state_attributes(self):
        """Return the state attributes of this device."""
        return {
            "bid": self._bid,
            "currency": self._currency_name,
            "code": self._currency_code,
            "table": self._table_name,
            "no": self._table_no,
            "tradingDate": self._trading_date,
            "effectiveDate": self._effective_date,
        }

    def update(self):
        self._updater.update()


class NBPUpdater:
    """Fetch newest rates from API."""

    def __init__(self, scan_interval):
        self.update = Throttle(scan_interval)(self._update)
        self.data = None
        self.error_msg = None

    def _update(self):
        self.error_msg = None
        address = f"{API_URL}"
        response = requests.get(address)
        if response.status_code == 200 and response.content.__len__() > 0:
            self.data = response.json()[0]
        else:
            msg = f"Error retrieving data. Status Code: {response.status_code}"
            self.error_msg = msg
