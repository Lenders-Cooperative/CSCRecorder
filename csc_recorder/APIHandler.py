import logging

import requests

from .constants import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger("csc-recorder")


class APIHandler:
    REQUEST_TIMEOUT = 10

    def __init__(self, host: str, username: str, password: str, headers: dict):
        self._host = host
        self._headers = headers
        self._username = username
        self.__password = password

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username

    def send_request(self, method, url, payload=None):
        LOGGER.info("Sending [%s] API call to [%s]", method, f"{self.host}{url}")

        try:
            response = requests.request(
                method,
                f"{self.host}{url}",
                headers=self._headers,
                timeout=self.REQUEST_TIMEOUT,
                data=payload,
                auth=(self.username, self.__password),
            )
            LOGGER.info(
                "Received [%s] response for [%s: %s]",
                response.status_code,
                method,
                f"{self.host}{url}",
            )

            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            LOGGER.error(
                "CSC API Failed. Received [%s] response for [%s: %s]",
                response.status_code,
                method,
                f"{self.host}{url}",
            )
            # TODO raise custom exception
            raise
