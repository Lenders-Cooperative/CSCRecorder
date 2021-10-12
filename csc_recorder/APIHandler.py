import requests


class APIHandler:
    REQUEST_TIMEOUT = 10

    def __init__(self, host: str, username: str, password: str, headers: dict):
        self.host = host
        self.headers = headers
        self.username = username
        self.password = password

    def send_request(self, method, url, payload=None):
        try:
            response = requests.request(
                method, 
                f"{self.host}{url}", 
                headers=self.headers, 
                timeout=self.REQUEST_TIMEOUT,
                data=payload,
                auth=(self.username, self.password)
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # TODO raise custom exception
            return e.response
        