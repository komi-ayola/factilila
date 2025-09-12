# entreprises/middleware.py
from django.db.models import Q
from .models import Entreprise, MembreEntreprise

class EntrepriseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.entreprise = None
        request.role_entreprise = None

        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            ent = None

            # 1) Entreprise active depuis le switch
            ent_id = request.session.get('active_entreprise_id')
            if ent_id:
                ent = (Entreprise.objects
                       .filter(
                           Q(id=ent_id),
                           Q(proprietaire=user) | Q(utilisateurs=user)
                       )
                       .first())

            # 2) Sinon, entreprise dont il est propriétaire
            if not ent:
                ent = Entreprise.objects.filter(proprietaire=user).first()

            # 3) Sinon, première où il est membre
            if not ent:
                ent = (Entreprise.objects
                       .filter(utilisateurs=user)
                       .first())

            request.entreprise = ent

            # Rôle courant
            if ent:
                if ent.proprietaire_id == user.id:
                    request.role_entreprise = 'admin'  # Owner = admin de fait
                else:
                    me = (MembreEntreprise.objects
                          .filter(entreprise=ent, user=user, is_active=True)
                          .only('role')
                          .first())
                    if me:
                        request.role_entreprise = me.role

        return self.get_response(request)
