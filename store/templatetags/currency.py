from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='rupee')
def rupee(value):
    if value is None:
        return '₹0.00'
    try:
        val = float(value) * getattr(settings, 'USD_TO_INR', 82)
        return f'₹{val:.2f}'
    except (ValueError, TypeError):
        return f'₹{value}'
