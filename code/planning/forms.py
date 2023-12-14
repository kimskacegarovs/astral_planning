from django import forms


class CSSClasses:
    DEFAULT = "bg-gray-600 text-white rounded-md p-2 m-2 placeholder-gray-400"


class CustomWidgetMixin:
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        attrs.setdefault('class', CSSClasses.DEFAULT)
        attrs.setdefault('placeholder', kwargs.pop('placeholder', ''))
        kwargs['attrs'] = attrs
        super().__init__(*args, **kwargs)


class TextWidget(CustomWidgetMixin, forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SelectWidget(CustomWidgetMixin, forms.Select):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = TextWidget(
            placeholder=kwargs.pop('placeholder', '')
        )
        super().__init__(*args, **kwargs)


class ChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = SelectWidget(
            placeholder=kwargs.pop('placeholder', '')
        )
        super().__init__(*args, **kwargs)


class LocationSearchForm(forms.Form):
    search = CharField(placeholder="Search for a location")


class LocationForm(forms.Form):
    entity_type = ChoiceField(placeholder="Type", choices=[("transport", "Transport"), ("shipment", "Shipment")])
    location = CharField(placeholder="Location")
    coordinates = CharField(placeholder="Coordinates")
