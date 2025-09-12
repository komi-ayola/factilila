# factures/forms.py
from django import forms
from django.forms import inlineformset_factory, formset_factory
from decimal import Decimal, InvalidOperation

from .models import Facture, LigneFacture, REMISE_CHOICES
from clients.models import Client          # <-- AJOUT
from produits.models import Produit        # <-- AJOUT


def _to_decimal(v, default='0.00'):
    """Accepte '1 234,56' ou '1234.56' → Decimal('1234.56')"""
    if v in (None, ''):
        return Decimal(default)
    if isinstance(v, (int, float, Decimal)):
        return Decimal(str(v))
    s = str(v).replace(' ', '').replace(',', '.')
    try:
        return Decimal(s)
    except (InvalidOperation, TypeError):
        raise forms.ValidationError("Valeur numérique invalide.")


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            'type_document', 'client', 'statut',
            'objet', 'tva', 'remise_globale_type', 'remise_globale_valeur',
            'frais_livraison',
        ]
    # widgets conservés
        widgets = {
            'type_document': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'objet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Objet de la facture/proforma"}),
            'tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'remise_globale_type': forms.Select(attrs={'class': 'form-select'}),
            'remise_globale_valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'frais_livraison': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):  # <-- AJOUT: entreprise dans __init__
        super().__init__(*args, **kwargs)
        if entreprise is not None:
            # Ne proposer que les clients de cette entreprise
            self.fields['client'].queryset = Client.objects.filter(entreprise=entreprise)

    def clean_tva(self):
        v = _to_decimal(self.cleaned_data.get('tva', '18.00'), default='18.00')
        if v < 0 or v > 100:
            raise forms.ValidationError("La TVA doit être comprise entre 0 et 100 %.") 
        return v

    def clean_remise_globale_valeur(self):
        v = _to_decimal(self.cleaned_data.get('remise_globale_valeur', '0.00'))
        if v < 0:
            raise forms.ValidationError("La remise globale ne peut pas être négative.")
        return v

    def clean_frais_livraison(self):
        v = _to_decimal(self.cleaned_data.get('frais_livraison', '0.00'))
        if v < 0:
            raise forms.ValidationError("Les frais de livraison ne peuvent pas être négatifs.")
        return v


class LigneFactureForm(forms.ModelForm):
    class Meta:
        model = LigneFacture
        fields = ['produit', 'quantite', 'prix_unitaire', 'remise_type', 'remise_valeur']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select produit-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': '1', 'step': '1'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control prix-input', 'step': '0.01', 'min': '0'}),
            'remise_type': forms.Select(choices=REMISE_CHOICES, attrs={'class': 'form-select remise-type'}),
            'remise_valeur': forms.NumberInput(attrs={'class': 'form-control remise-valeur', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, entreprise=None, **kwargs):  # <-- AJOUT: entreprise dans __init__
        super().__init__(*args, **kwargs)
        # Important : on rend le prix non requis (si vide → pris depuis le produit)
        self.fields['prix_unitaire'].required = False
        if entreprise is not None:
            # Ne proposer que les produits de cette entreprise
            self.fields['produit'].queryset = Produit.objects.filter(entreprise=entreprise)

    def clean_prix_unitaire(self):
        pu = self.cleaned_data.get('prix_unitaire')
        produit = self.cleaned_data.get('produit')
        # Si vide, on prendra le prix du produit
        if pu in (None, ''):
            if produit and getattr(produit, 'prix_unitaire', None) is not None:
                return produit.prix_unitaire
            return Decimal('0.00')
        return _to_decimal(pu)

    def clean_remise_valeur(self):
        t = self.cleaned_data.get('remise_type', 'aucune')
        v = _to_decimal(self.cleaned_data.get('remise_valeur', '0.00'))
        if v < 0:
            raise forms.ValidationError("La remise ne peut pas être négative.")
        if t == 'pourcentage' and v > 100:
            raise forms.ValidationError("Le pourcentage ne peut dépasser 100 %.") 
        return v


# formset pour la page d’ajout (libre, sans instance)
LigneFormSet = formset_factory(LigneFactureForm, extra=1, can_delete=True)

# inline formset pour la page de modification (lié à une instance)
LigneInlineFormSet = inlineformset_factory(
    Facture, LigneFacture,
    form=LigneFactureForm,
    extra=0,
    can_delete=True
)
