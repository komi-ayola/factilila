# core/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import date
from factures.models import Facture
from clients.models import Client
from django.http import HttpResponse


@login_required
def home(request):
    """Dashboard filtré par entreprise."""
    ent = getattr(request, 'entreprise', None)  # défini par le middleware plus bas
    if ent is None:
        # Si l'utilisateur n'a pas d'entreprise, on affiche des 0.
        context = dict(ca_mois=0, nb_factures=0, nb_proformas=0,
                       nb_clients=0, dernieres_factures=[], top_clients=[])
        return render(request, 'core/home.html', context)

    today = timezone.now().date()
    y, m = today.year, today.month

    factures_qs = (Facture.objects
                   .select_related('client')
                   .filter(entreprise=ent, type_document='facture')
                   .order_by('-date', '-id'))

    proformas_qs = (Facture.objects
                    .filter(entreprise=ent, type_document='proforma')
                    .order_by('-date', '-id'))

    clients_qs = Client.objects.filter(entreprise=ent)

    # CA du mois (TTC) : on somme via la méthode total_ttc() (Python-side)
    factures_mois = factures_qs.filter(date__year=y, date__month=m)
    ca_mois = sum([f.total_ttc() for f in factures_mois])

    # Compteurs
    nb_factures = factures_qs.count()
    nb_proformas = proformas_qs.count()
    nb_clients = clients_qs.count()

    # Dernières factures (10 dernières)
    dernieres_factures = factures_qs[:5]

    # Top 5 clients par CA (TTC) – simple agrégat Python
    # (Pour de gros volumes on pourra passer à un agrégat SQL)
    ca_par_client = {}
    for f in factures_qs:
        nom = f.client.nom
        ca_par_client[nom] = ca_par_client.get(nom, 0) + f.total_ttc()
    top_clients = sorted(
        [{'client__nom': k, 'ca': v} for k, v in ca_par_client.items()],
        key=lambda x: x['ca'],
        reverse=True
    )[:5]

    context = {
        'ca_mois': ca_mois,
        'nb_factures': nb_factures,
        'nb_proformas': nb_proformas,
        'nb_clients': nb_clients,
        'dernieres_factures': dernieres_factures,
        'top_clients': top_clients,
    }
    return render(request, 'core/home.html', context)



@login_required
def whoami(request):
    nom = request.user.username
    ent = getattr(request, 'entreprise', None)
    if ent:
        return HttpResponse(f"Connecté en tant que {nom} — Entreprise : {ent.nom_affichage or ent.nom} (id={ent.id})")
    return HttpResponse(f"Connecté en tant que {nom} — AUCUNE entreprise attachée.")
