import pytest
from .models import Location
from .types import (
    DataImportParsingOptions,
    RoutePolylineInput,
    RouteResponse,
    RoutePolylineOutput,
    EntityType,
)


class TestRoutePolylineInput:
    def test_as_tuple(self):
        route_input = RoutePolylineInput(start_lat=0.0, start_lon=0.0, end_lat=1.0, end_lon=1.0)
        result_tuple = route_input.as_tuple

        assert isinstance(result_tuple, tuple)
        assert len(result_tuple) == 4
        assert result_tuple == (0.0, 0.0, 1.0, 1.0)


class TestRouteResponse:
    def test_route_response_initialization(self):
        polyline_output = RoutePolylineOutput(polyline_array=[])
        route_response = RouteResponse(polyline=polyline_output, distance_km=10.0)

        assert isinstance(route_response.polyline, RoutePolylineOutput)
        assert route_response.distance_km == 10.0


class TestDataImportParsingOptions:
    def test_data_import_parsing_options(self):
        location = "Test Location"
        name = "Test Name"
        options = [
            Location(name="Location 1", latitude=1.23, longitude=4.56),
            Location(name="Location 2", latitude=7.89, longitude=10.11),
        ]
        parsing_options = DataImportParsingOptions(location=location, name=name, options=options)

        assert parsing_options.location == location
        assert parsing_options.name == name
        assert isinstance(parsing_options.options, list)
        assert all(isinstance(opt, Location) for opt in parsing_options.options)


class TestEntityType:
    @pytest.mark.parametrize(
        "entity_type, expected_choices",
        [
            (EntityType.TRANSPORT, [("transport", "Transport"), ("shipment", "Shipment")]),
            (EntityType.SHIPMENT, [("transport", "Transport"), ("shipment", "Shipment")]),
        ],
    )
    def test_entity_type_choices(self, entity_type, expected_choices):
        choices = entity_type.choices()

        assert isinstance(choices, list)
        assert choices == expected_choices
