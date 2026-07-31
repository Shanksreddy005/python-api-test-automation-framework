import json
import os

import pytest

from models.responses import User
from utils.assertions import assert_response_schema, assert_status_code

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
with open(os.path.join(SCHEMA_DIR, "user.json"), "r") as f:
    USER_SCHEMA = json.load(f)


@pytest.mark.api
@pytest.mark.smoke
def test_get_all_users(api_client):
    """Verify GET /users returns valid user list matching the schema."""
    response = api_client.get("/users")
    assert_status_code(response, 200)
    assert_response_schema(response, USER_SCHEMA)

    users = response.json()
    assert len(users) > 0
    # Validate first user
    user = User(**users[0])
    assert user.id > 0


@pytest.mark.api
def test_get_user_by_id(api_client):
    """Verify fetching an existing user by ID."""
    response = api_client.get("/users/1")
    assert_status_code(response, 200)
    user = User(**response.json())
    assert user.id == 1
