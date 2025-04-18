from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'prix_unitaire', 'description', 'remise_type', 'remise_valeur']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'remise_type': forms.Select(attrs={'class': 'form-control'}),
            'remise_valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }