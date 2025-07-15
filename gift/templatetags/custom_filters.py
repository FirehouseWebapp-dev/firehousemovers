from django import template

register = template.Library()

@register.filter
def nice_title(value):
    """Replace underscores with spaces and title-case the string."""
    return value.replace("_", " ").title()

@register.filter
def split_name(value):
    return value.split(" ")
