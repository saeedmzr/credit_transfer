import time

import requests
from requests import Timeout
from requests.exceptions import ChunkedEncodingError

from credit_transfer.settings.base import FCS_API_KEY


class BasePriceFetcher:
    def __init__(self):
        self.request = requests

    def send_request(self, method, **kwargs):
        url = kwargs['url']
        params = kwargs.get('params')
        headers = kwargs.get('headers')
        body = kwargs.get('body')
        for _ in range(3):
            try:
                if method == 'GET':
                    response = self.request.get(url, timeout=30, headers=headers, params=params)
                elif method == 'POST':
                    response = self.request.post(url, timeout=30, data=body, headers=headers, params=params)
                else:
                    raise Exception('Method must be GET or POST')

            except (Timeout, ConnectionError, ChunkedEncodingError,):
                time.sleep(3)
                continue
            return response.json()


class FCSapi(BasePriceFetcher):
    def __init__(self):
        super().__init__()
        self.base_url = "https://fcsapi.com/api-v3/crypto"
        self._api_key = FCS_API_KEY

    def get_crypto_price(self, symbol):
        options = {
            "access_key": self._api_key,
            "symbol": symbol,
            "type": "crypto",
        }
        return self.send_request('GET', url=self.base_url + '/latest', params=options).get("list", {}).get("response",
                                                                                                           {})

    def get_crypto_list(self):
        options = {
            "access_key": self._api_key,
            "type": "crypto",
        }
        return self.send_request('GET', url=self.base_url + '/list', params=options).get("response", {})


class CryptoFetcher:
    crypto_factory = {
        "fcs": FCSapi,
    }

    def __init__(self, type: str = "fcs"):
        self.fetcher = self.crypto_factory.get(type)()
