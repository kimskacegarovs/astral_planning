from validators import validate_coordinates_input
from django.forms import ValidationError
import pytest


class TestValidateCoordinatesInput:
    def test_valid_coordinates(self):
        validate_coordinates_input("40.7128,-74.0060")

    def test_invalid_coordinates(self):
        with pytest.raises(ValidationError):
            validate_coordinates_input("100,50")

        with pytest.raises(ValidationError):
            validate_coordinates_input("40.7128,-200")

        with pytest.raises(ValidationError):
            validate_coordinates_input("invalid")

        with pytest.raises(ValidationError):
            validate_coordinates_input("40.7128")
