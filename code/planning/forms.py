from django import forms
from .types import EntityType
from forms import CharField, NumberField, ChoiceField
from validators import validate_coordinates_input


class LocationSearchForm(forms.Form):
    search = CharField(placeholder="Search for a location")


class CreateEntityForm(forms.Form):
    entity_type = ChoiceField(placeholder="Type", choices=EntityType.choices())
    name = CharField(placeholder="Name")
    address = CharField(placeholder="Address")
    coordinates = CharField(placeholder="Coordinates", validators=[validate_coordinates_input])


class DeleteEntityForm(forms.Form):
    entity_type = ChoiceField(placeholder="Type", choices=EntityType.choices())
    id = CharField(placeholder="ID")


class OptimisePlanningForm(forms.Form):
    max_empty_km = NumberField(placeholder="Max empty km", required=False)
