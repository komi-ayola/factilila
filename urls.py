# factilila/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home(request):
    return redirect('liste_factures')  # on ira sur la liste des factures

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('clients/', include('clients.urls')),
    path('produits/', include('produits.urls')),
    path('factures/', include('factures.urls')),
]
