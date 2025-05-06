from django import template

register = template.Library()

@register.filter
def format_number(value):
    try:
        # Convertir en float et formater avec 2 décimales et séparateur d'espace
        return f"{float(value):,.2f}".replace(",", " ")
    except (ValueError, TypeError):
        return value