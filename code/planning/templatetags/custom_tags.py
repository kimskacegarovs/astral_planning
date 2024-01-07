from django import template
from django.utils.html import mark_safe
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def flag_svg(country_code):
    url = static(f"flags/4x3/{country_code}.svg")
    return mark_safe(f"<img src='{url}' alt='{country_code}' width='30' height='30' class='p-1'>")
