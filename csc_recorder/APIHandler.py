import logging.config

import requests

from .constants import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger("csc-recorder")


class APIHandler:
    REQUEST_TIMEOUT = 30

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

    def send_request(self, method, url, payload=None, log_config: dict = None, headers: dict = None):
        if not headers:
            headers = self._headers

        if self.__logging:
            LOGGER.info("Sending [%s] API call to [%s]", method, f"{self.host}{url}")

        log_entry = None

        if log_config:
            if (
                "model" not in log_config
                or "user" not in log_config
                or "sba_number" not in log_config
                or "timezone" not in log_config
            ):
                raise Exception("Invalid log dict")

        try:
            if log_config:
                log_entry = log_config["model"](
                    sba_number=log_config["sba_number"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                )

            response = requests.request(
                method,
                f"{self.host}{url}",
                headers=headers,
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

            if log_entry:
                log_entry.response_code = response.status_code
                log_entry.response_body = response.text
                log_entry.response_time = log_entry.request_time + response.elapsed
                log_entry.save()

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
                    response.status_code,
                    method,
                    f"{self.host}{url}",
                )

            raise Exception(f"Failed to get success response from CSC. Response: [{response.text}]") from excp
