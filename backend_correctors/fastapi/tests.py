import pytest
import requests

# Define the base URL of your API
BASE_URL = 'https://api.example.com/'

# Define the test data for different endpoints
ENDPOINT_TEST_DATA = [
    ('endpoint1', 200),  # Example: (endpoint, expected_status_code)
    ('endpoint2', 200),
    ('endpoint3', 404),  # Assuming this endpoint returns a 404
]


@pytest.mark.parametrize("endpoint, expected_status_code", ENDPOINT_TEST_DATA)
def test_api_endpoints(endpoint, expected_status_code):
    # Send a GET request to the endpoint
    response = requests.get(BASE_URL + endpoint)

    # Check if the response status code matches the expected status code
    assert response.status_code == expected_status_code, f"Unexpected status code for endpoint '{endpoint}'"
