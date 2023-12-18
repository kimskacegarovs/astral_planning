from django import forms
from forms import CharField, ChoiceField, NumberField
from validators import validate_coordinates_input

from .types import EntityType


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
