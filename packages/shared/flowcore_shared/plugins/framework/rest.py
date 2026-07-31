# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
import httpx
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Iterator

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# --- Authentication ---

class Authenticator(ABC):
    """Base class for REST API Authentication."""
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        pass

    def get_auth_params(self) -> Dict[str, str]:
        return {}

class ApiKeyAuthenticator(Authenticator):
    def __init__(self, key: str, header_name: str = "x-api-key"):
        self.key = key
        self.header_name = header_name

    def get_auth_headers(self) -> Dict[str, str]:
        return {self.header_name: self.key}

class BearerAuthenticator(Authenticator):
    def __init__(self, token: str):
        self.token = token

    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

class BasicAuthenticator(Authenticator):
    def __init__(self, username: str, password: str):
        import base64
        self.encoded = base64.b64encode(f"{username}:{password}".encode()).decode()

    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Basic {self.encoded}"}

class OAuth2Authenticator(Authenticator):
    """
    OAuth2 Architecture for retrieving and refreshing tokens.
    Implementations would store client_id, client_secret, refresh_token,
    and exchange them when expired.
    """
    def __init__(self, token_url: str, client_id: str, client_secret: str, refresh_token: str):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._access_token = None
        self._expires_at = 0

    def refresh(self):
        # Pseudo-code for OAuth2 refresh
        self._access_token = "mock_refreshed_token"
        self._expires_at = time.time() + 3600

    def get_auth_headers(self) -> Dict[str, str]:
        if not self._access_token or time.time() >= self._expires_at:
            self.refresh()
        return {"Authorization": f"Bearer {self._access_token}"}


# --- Pagination ---

class Paginator(ABC):
    """Base class for handling pagination."""
    @abstractmethod
    def next_page_token(self, response: httpx.Response) -> Optional[Any]:
        pass
        
    @abstractmethod
    def get_request_params(self, token: Any) -> Dict[str, Any]:
        pass

class CursorPaginator(Paginator):
    def __init__(self, cursor_field: str = "cursor", page_param: str = "cursor"):
        self.cursor_field = cursor_field
        self.page_param = page_param

    def next_page_token(self, response: httpx.Response) -> Optional[Any]:
        data = response.json()
        return data.get("pagination", {}).get(self.cursor_field)

    def get_request_params(self, token: Any) -> Dict[str, Any]:
        return {self.page_param: token} if token else {}

class OffsetPaginator(Paginator):
    def __init__(self, limit: int = 100, offset_param: str = "offset", limit_param: str = "limit"):
        self.limit = limit
        self.offset_param = offset_param
        self.limit_param = limit_param

    def next_page_token(self, response: httpx.Response) -> Optional[Any]:
        data = response.json()
        # Assume it returns a list of records
        records = data.get("data", [])
        if len(records) < self.limit:
            return None # End of pages
        # The token is the number of records seen so far
        return len(records)

    def get_request_params(self, token: Any) -> Dict[str, Any]:
        offset = token or 0
        return {self.offset_param: offset, self.limit_param: self.limit}

class PageNumberPaginator(Paginator):
    def __init__(self, page_param: str = "page"):
        self.page_param = page_param

    def next_page_token(self, response: httpx.Response) -> Optional[Any]:
        data = response.json()
        records = data.get("data", [])
        if not records:
            return None
        # The token is the current page number
        return response.request.url.params.get(self.page_param, 1)

    def get_request_params(self, token: Any) -> Dict[str, Any]:
        # Next token passed here is the current page, so we add 1
        page = int(token) + 1 if token else 1
        return {self.page_param: page}


# --- Rate Limiting & Retries ---

def get_retry_after(response: httpx.Response) -> float:
    """Extract Retry-After header and return seconds to wait."""
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            pass # Could be HTTP-date, ignoring for simplicity
    return 1.0 # Default fallback backoff

class RateLimitError(Exception):
    def __init__(self, retry_after: float):
        self.retry_after = retry_after

def retry_on_http_transient():
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, RateLimitError)),
        reraise=True
    )
