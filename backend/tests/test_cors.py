import pytest

pytestmark = pytest.mark.django_db


def test_preflight_allows_farm_context_header(client):
    response = client.options(
        "/api/v1/animals/",
        HTTP_ORIGIN="http://localhost:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-farm-id",
    )

    assert response.status_code == 200
    allowed_headers = response.headers["Access-Control-Allow-Headers"].lower().split(", ")
    assert "x-farm-id" in allowed_headers
