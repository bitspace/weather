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
