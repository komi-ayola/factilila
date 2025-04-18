from django import forms
from .models import Facture, LigneFacture
from clients.models import Client
from produits.models import Produit

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            'client', 'type_facture', 'statut',
            'remise_globale_type', 'remise_globale_valeur',
            'frais_livraison', 'tva'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'type_facture': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'remise_globale_type': forms.Select(attrs={'class': 'form-control'}),
            'remise_globale_valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'frais_livraison': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class LigneFactureForm(forms.ModelForm):
    class Meta:
        model = LigneFacture
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise_type', 'remise_valeur']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remise_type': forms.Select(attrs={'class': 'form-control'}),
            'remise_valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Vérifier si l'instance existe et a un produit associé
        if self.instance and self.instance.pk and self.instance.produit:
            self.initial['prix_unitaire'] = self.instance.produit.prix_unitaire