import requests
from .types import LocationSearchResult


class OpenStreetMapGeocodingService:
    def search(self, search: str) -> list[LocationSearchResult]:
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {"format": "json", "q": search}
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        results = [
            LocationSearchResult(
                display_name=result["display_name"],
                coordinates=f"{result['lat']}, {result['lon']}"
            )
            for result in response.json()
        ]
        return results


