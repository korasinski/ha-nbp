"""Constants for NBP - Narodowy Bank Polski integration."""

DEFAULT_NAME = "NBP"
VERSION = "0.0.1"

API_URL = "http://api.nbp.pl/api/exchangerates/tables/C?format=json"

CURRENCIES = [
    "AUD",
    "CAD",
    "CHF",
    "CZK",
    "DKK",
    "EUR",
    "GBP",
    "HUF",
    "JPY",
    "NOK",
    "SEK",
    "USD",
    "XDR",
]

ICONS = {
    "AUD": "mdi:currency-usd",  # "Australian Dollar"
    "CAD": "mdi:currency-cny",  # "Canadian Dollar"
    "CHF": "mdi:cash",  # "Swiss Franc"
    "CZK": "mdi:cash",  # "Czech Koruna"
    "DKK": "mdi:cash",  # "Danish Krone"
    "EUR": "mdi:currency-eur",  # "Euro"
    "GBP": "mdi:currency-gbp",  # "British Pound Sterling"
    "HUF": "mdi:cash-100",  # "Hungarian Forint"
    "JPY": "mdi:currency-jpy",  # "Japanese Yen"
    "NOK": "mdi:cash",  # "Norwegian Krone"
    "SEK": "mdi:cash",  # "Swedish Krona"
    "USD": "mdi:currency-usd",  # "United States Dollar"
    "XDR": "mdi:cash",  # "SDR (MFW)"
}
