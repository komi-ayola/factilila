# produits/models.py
from django.db import models
from decimal import Decimal
from decimal import Decimal
from entreprises.models import Entreprise

class Produit(models.Model):
    REMISE_CHOICES = [
        ('aucune', 'Aucune remise'),
        ('pourcentage', 'Pourcentage'),
        ('montant', 'Montant fixe'),
    ]
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='produits',
    )
    nom = models.CharField(max_length=120)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))  # ex: 18.00 = 18%
    type_remise = models.CharField(max_length=20, choices=REMISE_CHOICES, default='aucune')
    valeur_remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))  # % ou montant selon type
    description = models.CharField(max_length=255, blank=True, default="")
    def __str__(self):
        return self.nom
