# factures/utils.py
import re
from django.db import transaction
from django.db.models import IntegerField, Max
from django.db.models.functions import Substr, Cast
from django.utils import timezone
from django import template
from decimal import Decimal, InvalidOperation
from .models import Facture
from datetime import date
import unicodedata

register = template.Library()

def _max_prefix_from_python(numeros):
    """
    Fallback Python : lit une liste de numéros (strings) et retourne
    le max des 6 premiers chiffres quand le format est 'XXXXXX/...'.
    """
    max_val = 0
    pat = re.compile(r'^(\d{6})/')  # capture les 6 premiers digits avant le 1er '/'
    for num in numeros:
        if not num:
            continue
        m = pat.match(str(num))
        if m:
            try:
                val = int(m.group(1))
                if val > max_val:
                    max_val = val
            except ValueError:
                pass
    return max_val


# factures/utils.py
import re
import unicodedata

def _strip_accents(s: str) -> str:
    """Supprime les accents (É→E, ô→o…), conserve la ponctuation comme l'apostrophe."""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', s)
        if not unicodedata.combining(c)
    )

def _sanitize_for_numero(s: str) -> str:
    """
    Sanitize léger pour l'inclusion dans le numéro :
    - remplace '/' par '-' (car ton format utilise des '/')
    - supprime espaces en trop en bouts
    (on conserve l'apostrophe et le reste de la ponctuation)
    """
    return s.replace('/', '-').strip()

def code_entreprise(ent, *, upper: bool = True, prefer_attrs=('code', 'sigle', 'nom_affichage')) -> str:
    """
    Retourne le Suffixe “entreprise” pour la numérotation.

    Règles :
    1) Si ent.code / ent.sigle / ent.nom_affichage existe et n'est pas vide → on le renvoie **entièrement**,
       sans tronquer. On garde la ponctuation (ex. LILA'S). On peut forcer en MAJ avec upper=True.
    2) Sinon → on DERIVE un code court à partir de ent.nom_affichage ou ent.nom (2–4 lettres).

    NB : On remplace juste '/' par '-' pour éviter de casser le format 000001/25/F/SUFFIX.
    """
    if ent is None:
        return "EN"

    # 1) Valeur explicite → on respecte *entièrement*
    for attr in prefer_attrs:
        if hasattr(ent, attr):
            val = getattr(ent, attr, None)
            if val:
                # garde l'apostrophe, remplace juste '/', accents optionnels
                s = str(val)
                s = _strip_accents(s)     # enlève juste les accents, pas l'apostrophe
                s = _sanitize_for_numero(s)
                return s.upper() if upper else s

    # 2) Fallback : dérivation courte (2–4 lettres)
    nom = (
        getattr(ent, 'nom_affichage', None)
        or getattr(ent, 'nom', None)
        or 'ENT'
    )
    nom = _strip_accents(str(nom)).upper()
    # ne garder que les lettres pour le fallback
    letters = re.sub(r'[^A-Z]', '', nom)

    # 2–4 lettres max
    if not letters:
        return "EN"
    # tu peux ajuster 2 et 4 ; ici je garde 2–4 comme avant
    base = letters[:4]
    if len(base) < 2:
        base = (base + 'X' * 2)[:2]
    return base


def generer_numero(ent, type_doc, model_cls=None) -> str:
    """
    Génère le prochain numéro pour l'ENTREPRISE 'ent', le TYPE 'facture' ou 'proforma',
    au format NNNNNN/AA/F|P/CODE_ENT, séquencé par entreprise + type + année.
    """
    assert type_doc in ('facture', 'proforma')
    if model_cls is None:
        from .models import Facture as model_cls

    today = date.today()
    yy = str(today.year)[-2:]
    lettre = 'F' if type_doc == 'facture' else 'P'
    suffix = code_entreprise(ent)

    # On filtre sur l'entreprise, le type et l'année courante
    qs = (model_cls.objects
          .filter(entreprise=ent, type_document=type_doc, date__year=today.year)
          .exclude(numero__isnull=True)
          .exclude(numero__exact=''))

    # Essai DB: extraire les 6 premiers chiffres
    try:
        # num_int = CAST(SUBSTR(numero,1,6) AS INTEGER)
        agg = (qs
               .annotate(num_int=Cast(Substr('numero', 1, 6), IntegerField()))
               .aggregate(max_num=Max('num_int')))
        last = agg['max_num'] or 0
    except Exception:
        # Fallback: parsage Python si Cast/Substr ne sont pas supportés (ex. SQLite anciennes versions)
        last = 0
        for num in qs.values_list('numero', flat=True):
            if not num:
                continue
            m = re.match(r'(\d{1,6})/', num)
            if m:
                last = max(last, int(m.group(1)))

    next_num = f"{last + 1:06d}"
    return f"{next_num}/{yy}/{lettre}/{suffix}"

# factures/utils.py
from decimal import Decimal
try:
    from num2words import num2words
except ImportError:
    num2words = None

def montant_en_lettres(montant: Decimal) -> str:
    """
    Retourne le montant en toutes lettres en français (FCFA),
    arrondi à l'unité (pas de centimes généralement).
    """
    if montant is None:
        return ""
    # On arrondit à l'unité (FCFA)
    val = int(Decimal(montant).quantize(Decimal('1')))
    if num2words is None:
        # Fallback minimal si la lib n'est pas installée
        return f"{val} (en lettres indisponible)"
    txt = num2words(val, lang='fr')
    # Exemple : "un million deux cent trente-quatre mille" → capitalise 1ère lettre
    return txt[0].upper() + txt[1:]


@register.filter
def money(value, decimals=0):
    """Formatte en 'fr-FR' avec espace insécable milliers. Ex: 1 234 567,89"""
    try:
        v = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value
    q = Decimal(1) if int(decimals) == 0 else Decimal('1.' + '0'*int(decimals))
    v = v.quantize(q)
    s = f"{v:,.{int(decimals)}f}".replace(",", "X").replace(".", ",").replace("X", " ")
    return s

@register.filter
def pct(value):
    """Affiche 18% → '18 %'"""
    try:
        v = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value
    return f"{v.normalize()} %"

@register.filter
def milliers(value, decimals=0):
    """Alias money"""
    return money(value, decimals)