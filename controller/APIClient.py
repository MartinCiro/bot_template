from requests import request
from json import dumps
from requests.exceptions import RequestException
from controller.utils.Helpers import Helpers
from ast import literal_eval


class APIClient:
    def __init__(self, auth_token=None, timeout=90):
        helper = Helpers()
        self.base_url = helper.get_value("API", "host")
        self.dict_endpoints = literal_eval(helper.get_value("API", "endpoints"))
        self.auth_token = auth_token
        self.timeout = timeout

    def get_auth_header(self):
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    def get_status_connection(self):
        # Aquí podrías validar conectividad (ping, DNS, etc.)
        pass

    def request(self, endpoint, body=None, method="get"):
        self.get_status_connection()

        method = method.lower()
        is_body_method = method in ["post", "put", "patch"]

        headers = self.get_auth_header()
        if is_body_method:
            headers["Content-Type"] = "application/json"

        url = f"{self.base_url}/{endpoint}/"

        config = {
            "method": method,
            "url": url,
            "headers": headers,
            "timeout": self.timeout,
        }

        if is_body_method and body is not None:
            config["data"] = dumps(body)

        try:
            response = request(**config)
            response.raise_for_status()
            data = response.json()

            if "result" in data:
                return data["result"]
            else:
                raise ValueError("No se pudo obtener la información solicitada.")
        except RequestException as e:
            print(f"[ERROR] Fallo en '{method.upper()}' a {url}: {e}")
            raise
