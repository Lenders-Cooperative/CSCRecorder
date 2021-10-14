import base64
import logging.config
import urllib.error
import urllib.request as requests

from .constants import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger("csc-recorder")


class APIHandler:
    REQUEST_TIMEOUT = 10

    def __init__(self, host: str, username: str, password: str, headers: dict):
        self._host = host
        self._headers = headers
        self._username = username
        self.__authorization = base64.b64encode(
            f"{username}:{password}".encode()
        ).decode()

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username

    def _set_headers(self, request):
        request.add_header("Authorization", f"Basic {self.__authorization}")

        for key, value in self._headers.items():
            request.add_header(key, value)

    def send_request(self, method, url, payload=None):
        LOGGER.info("Sending [%s] API call to [%s]", method, f"{self.host}{url}")

        if payload and not isinstance(payload, bytes):
            payload = payload.encode()

        request = requests.Request(
            url=f"{self.host}{url}",
            data=payload,
            method=method,
        )
        self._set_headers(request)

        try:
            with requests.urlopen(request, timeout=self.REQUEST_TIMEOUT) as response:
                LOGGER.info(
                    "Received [%s] response for [%s: %s]",
                    response.code,
                    method,
                    f"{self.host}{url}",
                )

                if response.code not in range(200, 300):
                    LOGGER.error(
                        "CSC API Failed. Received [%s] response for [%s: %s]",
                        response.code,
                        method,
                        f"{self.host}{url}",
                    )

                    raise Exception(
                        f"Failed to get success response from CSC. Response: [{response.read()}]"
                    )

                response = response.read().decode()

                LOGGER.info(
                    "CSC Response for [%s: %s] -- [%s]",
                    method,
                    f"{self.host}{url}",
                    response,
                )

                return response
        except urllib.error.HTTPError as excp:
            raise Exception(f"Error from CSC. Error: [{excp}]") from excp
