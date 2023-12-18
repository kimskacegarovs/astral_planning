from css_classes import CSSClasses
from django import forms


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


class NumberField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = TextWidget(placeholder=kwargs.pop("placeholder", ""))
        super().__init__(*args, **kwargs)


class ChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs["widget"] = SelectWidget(placeholder=kwargs.pop("placeholder", ""))
        super().__init__(*args, **kwargs)
