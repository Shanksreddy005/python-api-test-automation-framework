import json
import os
from typing import Any, Dict

import pytest

from models.responses import Post
from utils.assertions import (
    assert_header,
    assert_response_schema,
    assert_response_time,
    assert_status_code,
)

# Load schemas and data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")

with open(os.path.join(DATA_DIR, "test_data.json"), "r") as f:
    TEST_DATA = json.load(f)

with open(os.path.join(SCHEMA_DIR, "post.json"), "r") as f:
    POST_SCHEMA = json.load(f)


@pytest.mark.smoke
@pytest.mark.api
def test_get_all_posts(api_client):
    """Verify GET /posts returns a valid list of posts matching the schema."""
    response = api_client.get("/posts")
    assert_status_code(response, 200)
    assert_response_time(response, 2000)
    assert_header(response, "Content-Type", "application/json; charset=utf-8")
    assert_response_schema(response, POST_SCHEMA)

    # Pydantic validation
    data = response.json()
    assert len(data) > 0
    # Validate the first item using Pydantic
    post = Post(**data[0])
    assert post.id > 0


@pytest.mark.smoke
def test_get_post_by_id(api_client):
    """Verify fetching an existing post by ID."""
    response = api_client.get("/posts/1")
    assert_status_code(response, 200)
    assert_response_schema(response, POST_SCHEMA)

    post = Post(**response.json())
    assert post.id == 1


@pytest.mark.negative
@pytest.mark.parametrize("invalid_id", [999999, "abc", -1, 0])
def test_get_post_invalid_id(api_client, invalid_id):
    """Verify API handles invalid and non-existent IDs gracefully."""
    response = api_client.get(f"/posts/{invalid_id}")
    assert_status_code(response, 404)


@pytest.mark.api
@pytest.mark.parametrize("payload", TEST_DATA["valid_posts"])
def test_create_post_valid(api_client, payload: Dict[str, Any]):
    """Verify POST /posts with valid data creates a resource."""
    response = api_client.post("/posts", json=payload)
    assert_status_code(response, 201)

    # Validation against Pydantic model
    post = Post(**response.json())
    assert post.title == payload["title"]
    assert post.userId == payload["userId"]


@pytest.mark.negative
@pytest.mark.parametrize("payload", TEST_DATA["invalid_posts"])
def test_create_post_invalid(api_client, payload: Dict[str, Any]):
    """Verify POST /posts with invalid data still responds appropriately."""
    response = api_client.post("/posts", json=payload)
    assert_status_code(response, 201)


@pytest.mark.api
def test_update_post(api_client):
    """Verify PUT /posts/1 updates the post."""
    payload = {"id": 1, "title": "updated title", "body": "updated body", "userId": 1}
    response = api_client.put("/posts/1", json=payload)
    assert_status_code(response, 200)
    post = Post(**response.json())
    assert post.title == "updated title"


@pytest.mark.api
def test_delete_post(api_client):
    """Verify DELETE /posts/1 successfully deletes."""
    response = api_client.delete("/posts/1")
    assert_status_code(response, 200)


@pytest.mark.api
def test_get_posts_filtered(api_client):
    """Verify filtering posts by userId."""
    response = api_client.get("/posts?userId=1")
    assert_status_code(response, 200)
    data = response.json()
    assert len(data) > 0
    for item in data:
        post = Post(**item)
        assert post.userId == 1
