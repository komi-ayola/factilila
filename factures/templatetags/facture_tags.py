from django import template
from num2words import num2words

register = template.Library()


@register.filter
def number_to_words(value):
    try:
        return num2words(int(value), lang='fr').capitalize()
    except (ValueError, TypeError):
        return str(value)