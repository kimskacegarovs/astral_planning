import requests
from .types import LocationSearchResult


class OpenStreetMapGeocodingService:
    BASE_URL = "https://nominatim.openstreetmap.org"

    def search(self, search: str) -> list[LocationSearchResult]:
        url = f"{self.BASE_URL}/search"
        params = {"format": "json", "q": search}
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = [
            LocationSearchResult(
                display_name=result["display_name"],
                coordinates=f"{result['lat']}, {result['lon']}"
            )
            for result in response.json()
        ]
        return results
