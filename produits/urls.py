from django.urls import path
from . import views

urlpatterns = [
    path('', views.produit_list, name='produit_list'),
    path('create/', views.produit_create, name='produit_create'),
    path('create-ajax/', views.produit_create_ajax, name='produit_create_ajax'),
    path('get_prix/<int:produit_id>/', views.get_prix_produit, name='get_prix_produit'),
    path('update/<int:produit_id>/', views.produit_update, name='produit_update'),
    path('delete/<int:produit_id>/', views.produit_delete, name='produit_delete'),
]