# main/templatetags/range_tags.py
from django import template
register = template.Library()

@register.filter
def to_int(value):
    return int(value)

@register.filter
def range(value, end):
    return range(int(value), int(end))
