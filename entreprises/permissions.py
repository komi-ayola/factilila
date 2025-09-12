# entreprises/permissions.py
from functools import wraps
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.db.models import Q
from .models import MembreEntreprise, Entreprise

def get_membership(user, entreprise):
    """
    Retourne un 'membership-like' compatible :
    - Propriétaire -> objet factice rôle 'admin'
    - Sinon -> MembreEntreprise (actif) ou None
    """
    if not user or not entreprise:
        return None
    if entreprise.proprietaire_id == getattr(user, 'id', None):
        class OwnerMembership:
            role = 'admin'
            is_active = True
        return OwnerMembership()
    return (MembreEntreprise.objects
            .filter(user=user, entreprise=entreprise, is_active=True)
            .first())

def require_member(view):
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        ent = getattr(request, 'entreprise', None)
        if not ent:
            return HttpResponseForbidden("Aucune entreprise active.")
        ms = get_membership(request.user, ent)
        if not ms:
            return HttpResponseForbidden("Accès refusé.")
        return view(request, *args, **kwargs)
    return _wrapped

def require_role(roles=('admin','staff')):
    roles = set(roles)
    def decorator(view):
        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            ent = getattr(request, 'entreprise', None)
            if not ent:
                return HttpResponseForbidden("Aucune entreprise active.")
            # Propriétaire = admin implicite
            if ent.proprietaire_id == getattr(request.user, 'id', None):
                return view(request, *args, **kwargs)
            ms = get_membership(request.user, ent)
            if not ms or ms.role not in roles:
                return HttpResponseForbidden("Accès refusé.")
            return view(request, *args, **kwargs)
        return _wrapped
    return decorator

def require_manage_members(view):
    """
    Réservé au propriétaire ou aux membres 'admin'
    """
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        ent = getattr(request, 'entreprise', None)
        if not ent:
            return HttpResponseForbidden("Aucune entreprise active.")
        if ent.proprietaire_id == getattr(request.user, 'id', None):
            return view(request, *args, **kwargs)
        ms = get_membership(request.user, ent)
        if not ms or ms.role != 'admin':
            return HttpResponseForbidden("Réservé aux administrateurs.")
        return view(request, *args, **kwargs)
    return _wrapped
