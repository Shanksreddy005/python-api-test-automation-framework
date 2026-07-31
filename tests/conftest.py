import logging

import pytest

from utils.api_client import APIClient


@pytest.fixture(scope="session")
def api_client():
    """
    Provides a session-level APIClient instance.
    This reuses the underlying requests.Session connection pool for all tests.
    """
    client = APIClient()
    yield client
    # Teardown: close the underlying session
    client.session.close()


@pytest.fixture
def test_user(api_client):
    """
    Setup: Create a test user.
    Teardown: Delete the created test user.
    """
    payload = {
        "name": "Test User",
        "username": "testuser_sdet",
        "email": "sdet.testuser@example.com",
    }

    logging.info("Setup: Creating a test user")
    response = api_client.post("/users", json=payload)

    # We assume successful creation for the fixture
    assert response.status_code == 201, "Failed to setup test user"
    user_data = response.json()
    user_id = user_data.get("id")

    # Provide the created user data to the test
    yield user_data

    # Teardown: clean up the resource
    if user_id:
        logging.info(f"Teardown: Deleting test user {user_id}")
        api_client.delete(f"/users/{user_id}")


@pytest.fixture
def test_post(api_client, test_user):
    """
    Setup: Create a test post associated with the test user.
    Teardown: Delete the created test post.
    """
    payload = {
        "title": "Automation Test Post",
        "body": "This post was created by automated API tests.",
        "userId": test_user.get("id"),
    }

    logging.info("Setup: Creating a test post")
    response = api_client.post("/posts", json=payload)

    assert response.status_code == 201, "Failed to setup test post"
    post_data = response.json()
    post_id = post_data.get("id")

    # Provide the created post data to the test
    yield post_data

    # Teardown: clean up the resource
    if post_id:
        logging.info(f"Teardown: Deleting test post {post_id}")
        api_client.delete(f"/posts/{post_id}")
