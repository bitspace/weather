import pytest
import httpx
from pytest_httpx import HTTPXMock
from weather import get_coordinates


def test_get_coordinates_returns_lat_lon(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://geocoding-api.open-meteo.com/v1/search?name=London&count=1&language=en&format=json",
        json={
            "results": [
                {"name": "London", "latitude": 51.5074, "longitude": -0.1278}
            ]
        },
    )
    lat, lon = get_coordinates("London")
    assert lat == pytest.approx(51.5074)
    assert lon == pytest.approx(-0.1278)


def test_get_coordinates_raises_for_unknown_city(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://geocoding-api.open-meteo.com/v1/search?name=Nonexistentville&count=1&language=en&format=json",
        json={},
    )
    with pytest.raises(ValueError, match="City 'Nonexistentville' not found"):
        get_coordinates("Nonexistentville")
