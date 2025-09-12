# factures/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal
from clients.models import Client
from produits.models import Produit
from entreprises.models import Entreprise

REMISE_CHOICES = [
    ('aucune', 'Aucune remise'),
    ('pourcentage', 'Pourcentage'),
    ('montant', 'Montant fixe'),
]

TYPE_CHOICES = [
        ('facture', 'Facture'),
        ('proforma', 'Proforma'),
    ]
STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyée', 'Envoyée'),
        ('payée', 'Payée'),
        ('convertie', 'Convertie'),  # ← on garde cet état
    ]
class SequenceNumero(models.Model):
    """
    Séquence de numérotation par année et type (facture/proforma).
    Garantit la continuité même en cas de suppression ou conversion.
    """
    annee = models.PositiveIntegerField()
    type_document = models.CharField(max_length=10, choices=TYPE_CHOICES)
    prochain = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('annee', 'type_document')

    def __str__(self):
        return f"{self.annee} - {self.type_document} : next={self.prochain}"


class Facture(models.Model):
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='factures',
    )
    type_document = models.CharField(max_length=10, choices=TYPE_CHOICES, default='facture')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='factures')
    date = models.DateField(default=timezone.now)
    numero = models.CharField(max_length=100, unique=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')

    # Globaux
    objet = models.CharField(max_length=255, blank=True)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    remise_globale_type = models.CharField(max_length=20, choices=REMISE_CHOICES, default='aucune')
    remise_globale_valeur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # 🔁 Lien de conversion : une facture convertie pointe vers sa proforma
    # et inversement proforma.facture_cible retourne L’UNIQUE facture liée
    est_convertie = models.BooleanField(default=False)
    source_proforma = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='facture_generee'
    )

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        num = self.numero or "—"
        return f"{self.get_type_document_display()} {num} - {self.client.nom}"
    # ---- Calculs
    def sous_total(self):
        total = Decimal('0.00')
        for l in self.lignes.all():
            total += l.montant_ht()
        return total.quantize(Decimal('0.01'))

    def montant_remise_globale(self):
        st = self.sous_total()
        if self.remise_globale_type == 'pourcentage':
            return (st * (self.remise_globale_valeur / Decimal('100'))).quantize(Decimal('0.01'))
        elif self.remise_globale_type == 'montant':
            return min(self.remise_globale_valeur, st).quantize(Decimal('0.01'))
        return Decimal('0.00')

    def total_ht(self):
        st = self.sous_total()
        rg = self.montant_remise_globale()
        total = st - rg + (self.frais_livraison or Decimal('0.00'))
        return max(total, Decimal('0.00')).quantize(Decimal('0.01'))

    def total_tva(self):
        base = self.total_ht()
        return (base * (self.tva / Decimal('100'))).quantize(Decimal('0.01'))

    def total_ttc(self):
        return (self.total_ht() + self.total_tva()).quantize(Decimal('0.01'))


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    # Remise par ligne
    remise_type = models.CharField(max_length=20, choices=REMISE_CHOICES, default='aucune')
    remise_valeur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    def montant_ht(self):
        q = Decimal(self.quantite or 0)
        p = self.prix_unitaire or Decimal('0.00')
        brut = q * p
        if self.remise_type == 'pourcentage':
            rem = brut * (self.remise_valeur / Decimal('100'))
        elif self.remise_type == 'montant':
            rem = min(self.remise_valeur, brut)
        else:
            rem = Decimal('0.00')
        net = max(brut - rem, Decimal('0.00'))
        return net.quantize(Decimal('0.01'))


class Paiement(models.Model):
    METHODE_CHOICES = [
        ('espèces', 'Espèces'),
        ('virement', 'Virement'),
        ('carte', 'Carte bancaire'),
        ('chèque', 'Chèque'),
    ]
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    date = models.DateField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    methode = models.CharField(max_length=50, choices=METHODE_CHOICES)

    def __str__(self):
        return f"{self.montant} FCFA - {self.facture.numero or '—'}"
