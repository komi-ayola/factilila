# entreprises/context_processors.py
from django.db.models import Q
from .models import Entreprise

def entreprises_accessibles(request):
    if request.user.is_authenticated:
        qs = (Entreprise.objects
              .filter(Q(proprietaire=request.user) | Q(utilisateurs=request.user))
              .distinct()
              .only('id', 'nom', 'nom_affichage'))
        return {'entreprises_accessibles': qs}
    return {}
