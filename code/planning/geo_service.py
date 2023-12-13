from .external_api import OpenStreetMapGeocodingService
from .types import LocationSearchResult


class GeoService:
    def search(self, search: str) -> list[LocationSearchResult]:
        return OpenStreetMapGeocodingService().search(search)