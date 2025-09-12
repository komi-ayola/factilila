# clients/urls.py
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.liste_clients, name='liste'),
    path('ajouter/', views.ajouter_client, name='ajouter'),
    path('<int:pk>/', views.detail_client, name='detail'),
    path('<int:pk>/modifier/', views.modifier_client, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_client, name='supprimer'),
]
