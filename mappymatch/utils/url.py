import functools as ft
from typing import List
from urllib.parse import urljoin


def _parse_uri(uri: str) -> str:
    return uri if uri.endswith("/") else f"{uri}/"


def multiurljoin(urls: List[str]) -> str:
    parsed_urls = [_parse_uri(uri) for uri in urls]
    return ft.reduce(urljoin, parsed_urls)
