# factures/admin.py
from django.contrib import admin
from .models import Facture, LigneFacture, Paiement
admin.site.register(Facture)
admin.site.register(LigneFacture)
admin.site.register(Paiement)
