from validators import validate_coordinates_input
from django.forms import ValidationError
import pytest


class TestValidateCoordinatesInput:
    def test_valid_coordinates(self):
        # Valid coordinates input
        valid_coordinates = "40.7128,-74.0060"  # Valid latitude and longitude for New York City

        # No ValidationError should be raised for valid input
        try:
            validate_coordinates_input(valid_coordinates)
        except ValidationError:
            pytest.fail("Unexpected ValidationError for valid coordinates")

    def test_invalid_coordinates(self):
        # Invalid coordinates inputs
        invalid_coordinates = [
            "100,50",  # Latitude out of range
            "40.7128,-200",  # Longitude out of range
            "invalid",  # Invalid format
            "40.7128",  # Missing longitude
        ]

        # Check if ValidationError is raised for each invalid input
        for invalid_input in invalid_coordinates:
            with pytest.raises(ValidationError):
                validate_coordinates_input(invalid_input)
