import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_coordinates(city: str) -> tuple[float, float]:
    """Return (latitude, longitude) for a city name."""
    response = httpx.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
    )
    response.raise_for_status()
    data = response.json()
    results = data.get("results")
    if not results:
        raise ValueError(f"City '{city}' not found")
    return results[0]["latitude"], results[0]["longitude"]


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_temperature(lat: float, lon: float) -> float:
    """Return current temperature in °C for the given coordinates."""
    response = httpx.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m",
        },
    )
    response.raise_for_status()
    data = response.json()
    return data["current"]["temperature_2m"]
