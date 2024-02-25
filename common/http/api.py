import requests

from common.http.request import GetBarDataRequest, GetSymbolRequest
from common.http.response import GetBarDataResponse, GetSymbolResponse


def get_bar_data(token: str, request: GetBarDataRequest) -> GetBarDataResponse:
    url = f"localhost:8080/api/data/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, json=request.to_dict())
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get data: {response.status_code} - {response.text}")
    get_data_response: GetBarDataResponse = response.json()
    return get_data_response


def get_symbol(token: str, request: GetSymbolRequest) -> GetSymbolResponse:
    url = f"localhost:8080/api/data/symbol"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, json=request.to_dict())
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get symbol: {response.status_code} - {response.text}")
    get_symbol_response: GetSymbolResponse = response.json()
    return get_symbol_response
