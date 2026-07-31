import json
import os

import pytest

from models.responses import Comment
from utils.assertions import assert_response_schema, assert_status_code

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")
with open(os.path.join(SCHEMA_DIR, "comment.json"), "r") as f:
    COMMENT_SCHEMA = json.load(f)


@pytest.mark.api
@pytest.mark.smoke
def test_get_comments_for_post(api_client):
    """Verify GET /posts/{id}/comments returns valid comments."""
    response = api_client.get("/posts/1/comments")
    assert_status_code(response, 200)
    assert_response_schema(response, COMMENT_SCHEMA)

    comments = response.json()
    assert len(comments) > 0
    # Validate first comment
    comment = Comment(**comments[0])
    assert comment.postId == 1
