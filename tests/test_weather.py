import re
import pytest
import httpx
from pytest_httpx import HTTPXMock
from typer.testing import CliRunner
from weather import get_coordinates
from weather import get_temperature
from weather import app

runner = CliRunner()


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


def test_get_temperature_returns_celsius(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r"https://api\.open-meteo\.com/v1/forecast"),
        json={
            "current": {
                "temperature_2m": 14.3,
            }
        },
    )
    temp = get_temperature(51.5074, -0.1278)
    assert temp == pytest.approx(14.3)


def test_cli_prints_temperature(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://geocoding-api.open-meteo.com/v1/search?name=Paris&count=1&language=en&format=json",
        json={"results": [{"name": "Paris", "latitude": 48.8566, "longitude": 2.3522}]},
    )
    httpx_mock.add_response(
        url=re.compile(r"https://api\.open-meteo\.com/v1/forecast"),
        json={"current": {"temperature_2m": 9.1}},
    )
    result = runner.invoke(app, ["Paris"])
    assert result.exit_code == 0
    assert "Paris" in result.output
    assert "9.1" in result.output


def test_cli_exits_nonzero_for_unknown_city(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://geocoding-api.open-meteo.com/v1/search?name=Fakecity&count=1&language=en&format=json",
        json={},
    )
    result = runner.invoke(app, ["Fakecity"])
    assert result.exit_code != 0
    combined = result.output + (result.stderr if hasattr(result, "stderr") and result.stderr else "")
    assert "not found" in combined.lower()


def test_cli_handles_multi_word_city(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=re.compile(r"https://geocoding-api\.open-meteo\.com.*name=New"),
        json={"results": [{"name": "New York", "latitude": 40.7128, "longitude": -74.0060}]},
    )
    httpx_mock.add_response(
        url=re.compile(r"https://api\.open-meteo\.com/v1/forecast"),
        json={"current": {"temperature_2m": 3.7}},
    )
    result = runner.invoke(app, ["New York"])
    assert result.exit_code == 0
    assert "3.7" in result.output
