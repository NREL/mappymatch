from functools import reduce
from typing import List
from urllib.parse import urljoin


def _parse_uri(uri: str) -> str:
    """Internal use."""
    return uri if uri.endswith("/") else f"{uri}/"


def multiurljoin(urls: List[str]) -> str:
    """
    Make a url from uri's.

    Args:
        urls: list of uri

    Returns:
        Url as uri/uri/...
    """
    parsed_urls = [_parse_uri(uri) for uri in urls]
    return reduce(urljoin, parsed_urls)
