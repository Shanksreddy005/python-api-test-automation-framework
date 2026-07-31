import pytest

from utils.assertions import assert_status_code


@pytest.mark.boundary
@pytest.mark.parametrize("title_len", [0, 1, 10000])
def test_post_title_boundaries(api_client, title_len: int):
    """Verify API handles extremely short and long titles."""
    long_string = "a" * title_len
    response = api_client.post(
        "/posts", json={"title": long_string, "body": "bar", "userId": 1}
    )
    assert_status_code(response, 201)
    assert response.json()["title"] == long_string


@pytest.mark.negative
@pytest.mark.parametrize(
    "special_payload",
    [
        {"title": None, "body": None, "userId": 1},
        {"title": "!@#$%^&*()_+~`|}{[]\\:;?><,./-=", "body": "bar", "userId": 1},
        {"title": True, "body": False, "userId": 1},
        [{"title": "foo"}, {"title": "bar"}],
        {"title": "", "body": "bar", "userId": 1},
    ],
)
def test_special_characters_and_types_in_body(api_client, special_payload):
    """Verify API handles special characters, nulls, booleans, and arrays as root."""
    response = api_client.post("/posts", json=special_payload)
    assert_status_code(response, 201)


@pytest.mark.boundary
def test_very_large_userid(api_client):
    """Verify API handles very large userId values."""
    large_id = 99999999999999999999999999
    response = api_client.post(
        "/posts", json={"title": "foo", "body": "bar", "userId": large_id}
    )
    assert_status_code(response, 201)
    # JSONPlaceholder converts extremely large numbers to scientific notation (float)
    assert float(response.json()["userId"]) == float(large_id)
