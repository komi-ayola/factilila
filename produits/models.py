from django.db import models

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    remise_type = models.CharField(
        max_length=15,  
        choices=[('aucune', 'Aucune'), ('pourcentage', '%'), ('montant', 'Montant fixe')],
        default='aucune'
    )
    remise_valeur = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom