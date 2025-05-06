from django.db import models
from django.core.validators import MinValueValidator
from clients.models import Client
from produits.models import Produit
import datetime

from decimal import Decimal

class CompteurFacture(models.Model):
    annee = models.IntegerField()  # Ex. 2025
    type_facture = models.CharField(max_length=10, choices=[
        ('facture', 'Facture'),
        ('proforma', 'Proforma'),
    ])
    dernier_numero = models.IntegerField(default=0)  # Dernier numéro utilisé

    class Meta:
        unique_together = ('annee', 'type_facture')  # Un compteur par année et type

    def incrementer(self):
        self.dernier_numero += 1
        self.save()
        return self.dernier_numero

class Facture(models.Model):
    TYPE_FACTURE_CHOICES = [
        ('facture', 'Facture'),
        ('proforma', 'Proforma'),
    ]
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
        ('converti', 'Converti'),
    ]
    REMISE_CHOICES = [
        ('aucune', 'Aucune'),
        ('pourcentage', 'Pourcentage'),
        ('montant_fixe', 'Montant fixe'),
    ]

    numero = models.CharField(max_length=20, unique=True, blank=True)
    date = models.DateField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    objet = models.CharField(max_length=200, blank=True, null=True) 
    type_facture = models.CharField(max_length=10, choices=TYPE_FACTURE_CHOICES, default='facture')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='brouillon')
    remise_globale_type = models.CharField(max_length=20, choices=REMISE_CHOICES, default='aucune')
    remise_globale_valeur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)  # Ex. 18% TVA

    def save(self, *args, **kwargs):
        if not self.numero:  # Générer le numéro si non défini
            annee = datetime.datetime.now().year % 100  # Ex. 25 pour 2025
            type_facture = self.type_facture
            compteur, created = CompteurFacture.objects.get_or_create(
                annee=annee,
                type_facture=type_facture,
                defaults={'dernier_numero': 0}
            )
            numero_ordre = compteur.incrementer()
            prefixe = 'F' if type_facture == 'facture' else 'P'
            self.numero = f"{numero_ordre:06d}/{annee}/{prefixe}/LILA'S"
        super().save(*args, **kwargs)

    @property
    def sous_total(self):
        total =sum(Decimal(str(ligne.calculer_total())) for ligne in self.lignefacture_set.all())
        return total

    @property
    def total_sans_tva(self):
        total = self.sous_total
        if self.remise_globale_type == 'pourcentage':
            total -= total * (self.remise_globale_valeur / 100)
        elif self.remise_globale_type == 'montant_fixe':
            total -= self.remise_globale_valeur
        total += self.frais_livraison
        return total

    @property
    def montant_tva(self):
        return self.total_sans_tva * (self.tva / 100)

    @property
    def total_ttc(self):
        return self.total_sans_tva + self.montant_tva

    def calculer_remise_globale(self):
        sous_total = self.calculer_sous_total()
        if self.remise_globale_type == 'pourcentage':
            return (sous_total * self.remise_globale_valeur) / 100
        elif self.remise_globale_type == 'montant_fixe':
            return self.remise_globale_valeur
        return 0

       
    def __str__(self):
        return f"Facture #{self.numero} - {self.client}"


class LigneFacture(models.Model):
  
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    def __str__(self):
        return f"{self.produit.nom} (x{self.quantite})"
    def calculer_total(self):
        total = self.quantite * self.prix_unitaire
        return total    
    