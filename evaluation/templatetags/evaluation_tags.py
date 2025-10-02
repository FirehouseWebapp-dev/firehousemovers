from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup a key in a dictionary."""
    return dictionary.get(key)

@register.filter
def startswith(value, arg):
    """
    Template filter to check if a string starts with a given prefix.
    Handles None values and type conversion safely.
    """
    if not value or not arg:
        return False
    try:
        return str(value).startswith(str(arg))
    except (TypeError, AttributeError):
        return False
