# entreprises/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "entreprises"

urlpatterns = [
    path('profil/', views.profil_entreprise, name='profil'),
    path('signup/', views.signup, name='signup'),  
    #path('changer/<int:pk>/', views.changer_entreprise, name='changer'),
    path('membres/', views.gestion_membres, name='gestion_membres'),
    path('membres/ajouter/', views.ajouter_membre, name='ajouter_membre'),
    path('membres/<int:membre_id>/role/', views.changer_role, name='changer_role'),
    path('membres/<int:membre_id>/retirer/', views.retirer_membre, name='retirer_membre'),
    path('switch/', views.switch_entreprise, name='switch'),

    path('membres/creer-utilisateur/', views.creer_utilisateur_membre, name='creer_utilisateur_membre'),

    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
