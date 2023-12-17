from .external_api import OpenStreetMapGeocodingService, OpenRouteService
from .types import LocationSearchResult, RoutePolylineInput, RoutePolylineOutput


class GeoService:
    def search(self, search: str) -> list[LocationSearchResult]:
        return OpenStreetMapGeocodingService().search(search)

    def get_route_polyline(self, route_input: RoutePolylineInput) -> RoutePolylineOutput | None:
        return OpenRouteService().get_route_polyline(route_input=route_input)
