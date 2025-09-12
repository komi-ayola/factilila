from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()

def _to_decimal(x):
    if x is None or x == "":
        return Decimal("0")
    try:
        if isinstance(x, Decimal):
            return x
        # remplace les espaces en milliers et virgules par points
        s = str(x).replace("\xa0", " ").replace(" ", "").replace(",", ".")
        return Decimal(s)
    except Exception:
        return Decimal("0")

def _format_fr(value: Decimal, decimals: int = 2) -> str:
    """
    Format français : séparateur de milliers = espace, séparateur décimal = virgule.
    Ex: 1234567.8 -> "1 234 567,80"
    """
    if value is None:
        value = Decimal("0")
    if not isinstance(value, Decimal):
        value = _to_decimal(value)
    q = value.quantize(Decimal("1." + "0" * decimals), rounding=ROUND_HALF_UP) if decimals > 0 else value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    s = f"{q:.{decimals}f}"
    if "." in s:
        int_part, dec_part = s.split(".")
    else:
        int_part, dec_part = s, ""
    # regrouper par milliers sur int_part
    int_part = int(int_part)
    int_part_str = f"{int_part:,}".replace(",", " ")
    if decimals > 0:
        return f"{int_part_str},{dec_part}"
    return int_part_str

@register.filter(name="format_fr")
def format_fr(value, decimals=2):
    """
    {{ value|format_fr }} ou {{ value|format_fr:0 }}
    """
    try:
        decimals = int(decimals)
    except Exception:
        decimals = 2
    return _format_fr(_to_decimal(value), decimals)

@register.filter(name="milliers")
def milliers(value, decimals=0):
    """Abrégé pour format en milliers (par défaut sans décimales)."""
    return format_fr(value, decimals)

@register.filter(name="money")
def money(value, decimals=0):
    """Affichage FCFA : ex 1234567 -> '1 234 567 FCFA'"""
    return f"{format_fr(value, decimals)} FCFA"

@register.filter(name="pct")
def pct(value, decimals=2):
    """Affichage d’un pourcentage : 18 -> '18,00 %'"""
    return f"{format_fr(value, decimals)} %"

@register.filter(name="mul")
def mul(a, b):
    """Multiplication dans les templates : {{ qte|mul:prix }}"""
    da = _to_decimal(a)
    db = _to_decimal(b)
    return da * db
