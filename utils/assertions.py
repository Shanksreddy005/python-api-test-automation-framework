import logging
from typing import Any, Dict

import jsonschema
from requests import Response

from utils.exceptions import InvalidResponseError, SchemaValidationError

logger = logging.getLogger("api_client.assertions")


def log_and_assert(condition: bool, message: str) -> None:
    """Evaluates a condition, logs the assertion attempt, and asserts it."""
    if condition:
        logger.debug(f"Assertion passed: {message}")
    else:
        logger.error(f"Assertion failed: {message}")
    assert condition, message


def assert_status_code(response: Response, expected_status_code: int) -> None:
    """Asserts that the response status code matches the expected status code."""
    message = (
        f"Expected status code {expected_status_code}, but got {response.status_code}"
    )
    log_and_assert(response.status_code == expected_status_code, message)


def assert_response_time(response: Response, max_ms: int) -> None:
    """Asserts that the response time is less than or equal to max_ms."""
    time_taken = getattr(response, "response_time_ms", 0)
    message = f"Expected response time <= {max_ms}ms, but got {time_taken:.2f}ms"
    log_and_assert(time_taken <= max_ms, message)


def assert_header(response: Response, header: str, expected_value: str) -> None:
    """Asserts that a specific header matches the expected value."""
    actual_value = response.headers.get(header)
    message = (
        f"Expected header '{header}' to be '{expected_value}', got '{actual_value}'"
    )
    log_and_assert(actual_value == expected_value, message)


def assert_empty_response(response: Response) -> None:
    """Asserts that the response body is empty."""
    content = response.text.strip()
    # Handle cases where an empty array or object is technically empty, or just no content
    is_empty = content in ("", "{}", "[]")
    message = f"Expected empty response, got '{content}'"
    log_and_assert(is_empty, message)


def assert_json_value(response: Response, key: str, expected_value: Any) -> None:
    """Asserts that a specific key in the JSON response matches the expected value."""
    try:
        data = response.json()
        actual_value = data.get(key)
        message = (
            f"Expected JSON key '{key}' to be '{expected_value}', got '{actual_value}'"
        )
        log_and_assert(actual_value == expected_value, message)
    except ValueError:
        raise InvalidResponseError("Response is not valid JSON")


def assert_json_list_length(response: Response, expected_length: int) -> None:
    """Asserts that the JSON response is a list of a specific length."""
    try:
        data = response.json()
        if not isinstance(data, list):
            raise InvalidResponseError("Response is not a list")
        actual_length = len(data)
        message = f"Expected list length {expected_length}, got {actual_length}"
        log_and_assert(actual_length == expected_length, message)
    except ValueError:
        raise InvalidResponseError("Response is not valid JSON")


def assert_response_schema(response: Response, schema: Dict[str, Any]) -> None:
    """
    Asserts that the JSON response matches the provided JSON schema.
    If the response is a list, validates the first item.
    """
    try:
        data = response.json()
    except ValueError:
        raise InvalidResponseError("Response is not valid JSON for schema validation")

    target_data = data[0] if isinstance(data, list) and data else data

    try:
        jsonschema.validate(instance=target_data, schema=schema)
        logger.debug("Schema validation passed.")
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}")
        raise SchemaValidationError(f"Schema validation error: {e.message}")
