import logging.config

import requests

from .constants import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger("csc-recorder")


class APIHandler:
    REQUEST_TIMEOUT = 10

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        headers: dict,
        logging: bool = True,
    ):
        self._host = host
        self._headers = headers
        self._username = username
        self.__password = password
        self.__logging = logging

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username

    def send_request(self, method, url, payload=None):
        if self.__logging:
            LOGGER.info("Sending [%s] API call to [%s]", method, f"{self.host}{url}")

        try:
            request = requests.request(
                method,
                f"{self.host}{url}",
                headers=self._headers,
                timeout=self.REQUEST_TIMEOUT,
                data=payload,
                auth=(self.username, self.__password),
            )

            if self.__logging:
                LOGGER.info(
                    "Received [%s] response for [%s: %s]",
                    response.status_code,
                    method,
                    f"{self.host}{url}",
                )

            response.raise_for_status()

            response = response.text

            if self.__logging:
                LOGGER.info(
                    "CSC Response for [%s: %s] -- [%s]",
                    method,
                    f"{self.host}{url}",
                    response,
                )

            return response
        except requests.HTTPError as excp:
            if self.__logging:
                LOGGER.error(
                    "CSC API Failed. Received [%s] response for [%s: %s]",
                    response.code,
                    method,
                    f"{self.host}{url}",
                )

            raise Exception(
                f"Failed to get success response from CSC. Response: [{response.text}]"
            ) from excp
