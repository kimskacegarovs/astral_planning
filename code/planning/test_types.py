import pytest
from .types import (
    DataImportParsingOptions,
    LocationSearchResult,
    RoutePolylineInput,
    RouteResponse,
    RoutePolylineOutput,
    EntityType,
)


class TestLocationSearchResult:
    def test_as_dict(self):
        sample_location = LocationSearchResult(display_name="Sample Location", coordinates="1.234,5.678")
        result_dict = sample_location.as_dict

        assert isinstance(result_dict, dict)
        assert "display_name" in result_dict
        assert "coordinates" in result_dict
        assert result_dict["display_name"] == "Sample Location"
        assert result_dict["coordinates"] == "1.234,5.678"


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
            LocationSearchResult(display_name="Location 1", coordinates="1.23,4.56"),
            LocationSearchResult(display_name="Location 2", coordinates="7.89,10.11"),
        ]
        parsing_options = DataImportParsingOptions(location=location, name=name, options=options)

        assert parsing_options.location == location
        assert parsing_options.name == name
        assert isinstance(parsing_options.options, list)
        assert all(isinstance(opt, LocationSearchResult) for opt in parsing_options.options)


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
