from .external_api import OpenStreetMapGeocodingService, OpenRouteService
from .types import LocationSearchResult, RoutePolylineInput, RouteResponse


class GeoService:
    def search(self, search: str) -> list[LocationSearchResult]:
        return OpenStreetMapGeocodingService().search(search)

    def get_route(self, route_input: RoutePolylineInput) -> RouteResponse:
        return OpenRouteService().get_route(route_input=route_input)
