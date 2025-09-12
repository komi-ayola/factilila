# entreprises/templatetags/entreprises_tags.py
from django import template
from entreprises.models import MembreEntreprise

register = template.Library()

@register.filter
def role_badge(role):
    """
    Rend un petit badge Bootstrap selon le rôle.
    Usage: {{ m.role|role_badge|safe }}
    """
    mapping = {
        'admin':   ('Administrateur', 'primary'),
        'staff':   ('Utilisateur',    'success'),
        'lecture': ('Lecture',        'secondary'),
    }
    label, cls = mapping.get(role, (role or '—', 'secondary'))
    return f'<span class="badge bg-{cls}">{label}</span>'

@register.simple_tag(takes_context=True)
def can_manage_members(context):
    """
    Retourne True si l'utilisateur courant peut gérer les membres de l'entreprise active.
    Propriétaire = admin implicite.
    """
    request = context.get('request')
    if not request:
        return False
    user = getattr(request, 'user', None)
    ent = getattr(request, 'entreprise', None)

    if not user or not user.is_authenticated or not ent:
        return False

    # Le propriétaire = admin
    if getattr(ent, 'proprietaire_id', None) == user.id:
        return True

    # Sinon, vérifie MembreEntreprise avec rôle admin actif
    return MembreEntreprise.objects.filter(
        entreprise=ent, user=user, role='admin', is_active=True
    ).exists()
