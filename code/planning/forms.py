from django import forms


class LocationSearchForm(forms.Form):
    search = forms.CharField(label="Search location", max_length=100)
