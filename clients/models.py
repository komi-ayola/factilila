# clients/models.py
from django.db import models
from entreprises.models import Entreprise

class Client(models.Model):
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='clients',
    )
    nom = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom
