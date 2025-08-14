from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def startswith(value: str, prefix: str) -> bool:
    return value.startswith(prefix)

@register.filter(name="repeat")
def repeat(value, count):
    try:
        n = int(count or 0)
    except (TypeError, ValueError):
        n = 0
    return mark_safe(str(value) * max(n, 0))

@register.filter
def pct(done, total):
    try:
        done = int(done or 0)
        total = int(total or 0)
        return int(round((done / total) * 100)) if total else 100
    except Exception:
        return 0