from django.contrib import admin
from django.urls import path
from facture_project import views
from factures import views as facture_views
from clients import views as client_views
from produits import views as produit_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # URL racine vers la page d'accueil
    # URLs pour l'application clients
    path('clients/', client_views.client_list, name='client_list'),
    path('clients/create/', client_views.client_create, name='client_create'),
    path('clients/create-ajax/', client_views.client_create_ajax, name='client_create_ajax'),
    path('clients/update/<int:client_id>/', client_views.client_update, name='client_update'),
    path('clients/delete/<int:client_id>/', client_views.client_delete, name='client_delete'),
    # URLs pour l'application produits
    path('produits/', produit_views.produit_list, name='produit_list'),
    path('produits/create/', produit_views.produit_create, name='produit_create'),
    path('produits/create-ajax/', produit_views.produit_create_ajax, name='produit_create_ajax'),
    path('produits/get_prix/<int:produit_id>/', produit_views.get_prix_produit, name='get_prix_produit'),
    path('produits/update/<int:produit_id>/', produit_views.produit_update, name='produit_update'),
    path('produits/delete/<int:produit_id>/', produit_views.produit_delete, name='produit_delete'),
    # URLs pour l'application factures
    path('factures/', facture_views.facture_list, name='facture_list'),
    path('factures/proformas/', facture_views.proforma_list, name='proforma_list'),
    path('factures/create/', facture_views.facture_create, name='facture_create'),
    path('factures/detail/<int:pk>/', facture_views.facture_detail, name='facture_detail'),
    path('factures/delete/<int:pk>/', facture_views.facture_delete, name='facture_delete'),
    path('factures/factures/<int:pk>/update/', facture_views.facture_update, name='facture_update'),
    path('factures/proformas/<int:pk>/convert/', facture_views.proforma_to_facture, name='proforma_to_facture'),
]