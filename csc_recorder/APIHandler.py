import requests


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
        try:
            response = requests.request(
                method,
                f"{self.host}{url}",
                headers=self._headers,
                timeout=self.REQUEST_TIMEOUT,
                data=payload,
                auth=(self.username, self.__password),
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # TODO raise custom exception
            return e.response
