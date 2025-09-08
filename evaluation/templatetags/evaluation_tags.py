from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Template filter to lookup a key in a dictionary."""
    return dictionary.get(key)

@register.filter
def startswith(value, arg):
    """Template filter to check if a string starts with a given prefix."""
    if not value or not arg:
        return False
    return str(value).startswith(str(arg))
