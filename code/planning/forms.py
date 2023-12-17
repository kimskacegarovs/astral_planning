from django import forms
from .types import EntityType


class CSSClasses:
    DEFAULT = "bg-gray-600 text-white rounded-md p-2 m-2 placeholder-gray-400"


class CustomWidgetMixin:
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs.setdefault("class", CSSClasses.DEFAULT)
        attrs.setdefault("placeholder", kwargs.pop("placeholder", ""))
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)


class TextWidget(CustomWidgetMixin, forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SelectWidget(CustomWidgetMixin, forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = TextWidget(placeholder=kwargs.pop("placeholder", ""))
        super().__init__(*args, **kwargs)


class ChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = SelectWidget(placeholder=kwargs.pop("placeholder", ""))
        super().__init__(*args, **kwargs)


class LocationSearchForm(forms.Form):
    search = CharField(placeholder="Search for a location")


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


class LocationForm(forms.Form):
    entity_type = ChoiceField(placeholder="Type", choices=EntityType.choices())
    name = CharField(placeholder="Name")
    address = CharField(placeholder="Address")
    coordinates = CharField(placeholder="Coordinates", validators=[validate_coordinates_input])


class DeleteEntityForm(forms.Form):
    entity_type = ChoiceField(placeholder="Type", choices=EntityType.choices())
    id = CharField(placeholder="ID")
