from django import forms


class TextWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        attrs.setdefault('class', 'bg-gray-600 text-white rounded-md p-2 m-2 placeholder-gray-400')
        attrs.setdefault('placeholder', kwargs.pop('placeholder', ''))
        kwargs['attrs'] = attrs
        super().__init__(*args, **kwargs)


class CharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = TextWidget(
            placeholder=kwargs.pop('placeholder', '')
        )
        super().__init__(*args, **kwargs)


class LocationSearchForm(forms.Form):
    search = CharField(placeholder="Search for a location")


class LocationForm(forms.Form):
    location = CharField(placeholder="Location")
    coordinates = CharField(placeholder="Coordinates")
