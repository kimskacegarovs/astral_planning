from django import forms


def validate_coordinates_input(value):
    try:
        latitude, longitude = value.split(",")
        latitude = float(latitude)
        longitude = float(longitude)
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be in range [-90, 90]")
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be in range [-180, 180]")
    except ValueError as e:
        raise forms.ValidationError(str(e))
