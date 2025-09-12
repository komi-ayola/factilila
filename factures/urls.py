# factures/urls.py
from django.urls import path
from . import views

app_name = 'factures'

urlpatterns = [
    # Listes
    path('', views.liste_factures, name='liste'),
    path('proformas/', views.liste_proformas, name='liste_proformas'),

    # Détail
    path('<int:pk>/', views.detail_facture, name='detail'),

    # CRUD
    path('ajouter/', views.ajouter_facture, name='ajouter'),
    path('<int:pk>/modifier/', views.modifier_facture, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_facture, name='supprimer'),

    # Conversion proforma -> facture
    path('proformas/<int:pk>/convertir/', views.convertir_proforma, name='convertir'),

    path('<int:pk>/pdf/', views.document_pdf, name='pdf'),
]
