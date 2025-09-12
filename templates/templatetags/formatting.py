# factures/templatetags/formatting.py
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

def _fmt_fr(value, decimals=2):
    try:
        v = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return "0"
    s = f"{v:,.{decimals}f}"
    s = s.replace(",", " ").replace(".", ",")
    return s

@register.filter
def format_fr(value, decimals=2):
    return _fmt_fr(value, decimals)

@register.filter
def fcfa(value, decimals=2):
    return f"{_fmt_fr(value, decimals)} FCFA"
