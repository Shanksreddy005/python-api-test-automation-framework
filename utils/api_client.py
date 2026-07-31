import logging
import os
import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config
from utils.exceptions import APIRequestError

# Setup logging directory
os.makedirs(config.LOG_DIR, exist_ok=True)
log_file = os.path.join(config.LOG_DIR, "api.log")

# Configure structured logger
logger = logging.getLogger("api_client")
logger.setLevel(config.LOG_LEVEL)

file_handler = logging.FileHandler(log_file)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(file_handler)


class APIClient:
    """
    A robust API client for making HTTP requests with connection pooling,
    retry logic, configurable timeouts, and structured logging.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.BASE_URL
        self.timeout = config.TIMEOUT
        self.session = requests.Session()

        # Configure Retry Strategy
        retry_strategy = Retry(
            total=config.RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "OPTIONS",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            ],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Register Response Hooks
        self.session.hooks["response"] = [self._response_hook]

    def _response_hook(
        self, response: requests.Response, *args: Any, **kwargs: Any
    ) -> None:
        """
        Hook executed automatically after every request to log the raw status.
        The full structured logging is handled in _request.
        """
        pass

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> requests.Response:
        """
        Internal method to execute HTTP requests with logging and error handling.
        """
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)

        # Structured request logging
        logger.info(f"REQUEST | Method: {method} | URL: {url}")
        if "headers" in kwargs:
            logger.debug(f"REQUEST | Headers: {kwargs['headers']}")
        if "json" in kwargs:
            logger.info(f"REQUEST | Payload (JSON): {kwargs['json']}")
        if "data" in kwargs:
            logger.info(f"REQUEST | Payload (Data): {kwargs['data']}")
        if "params" in kwargs:
            logger.info(f"REQUEST | Query Params: {kwargs['params']}")

        start_time = time.perf_counter()
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.error(f"EXCEPTION | Request failed: {e}")
            raise APIRequestError(f"Request to {url} failed: {e}") from e

        end_time = time.perf_counter()

        # Calculate response time in milliseconds
        response.response_time_ms = (end_time - start_time) * 1000

        # Structured response logging
        logger.info(
            f"RESPONSE | Status: {response.status_code} | "
            f"Time: {response.response_time_ms:.2f}ms | URL: {response.url}"
        )
        logger.debug(f"RESPONSE | Headers: {response.headers}")

        try:
            logger.debug(f"RESPONSE | Body: {response.json()}")
        except ValueError:
            logger.debug(f"RESPONSE | Body: {response.text}")

        return response

    def get(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)
