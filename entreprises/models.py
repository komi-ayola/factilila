# entreprises/models.py
from django.conf import settings
from django.db import models

def logo_upload_path(instance, filename):
    return f"logos_entreprises/{instance.pk}/{filename}"

class Entreprise(models.Model):
    proprietaire = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entreprise'
    )
    nom = models.CharField(max_length=255)
    nom_affichage = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nom tel qu'il apparaît sur les PDF (ex: LILA'S)"
    )
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, default='Togo')
    telephone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)
    nom_signataire = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nom du directeur ou signataire"
    )

    # multi-utilisateurs par entreprise
    utilisateurs = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='MembreEntreprise',
        related_name='entreprises'
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"

    def __str__(self):
        return self.nom_affichage or self.nom


class MembreEntreprise(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'
    ROLE_LECTURE = 'lecture'
    ROLES = (
        (ROLE_ADMIN, 'Administrateur'),
        (ROLE_STAFF, 'Utilisateur (écriture)'),
        (ROLE_LECTURE, 'Lecture seule'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default=ROLE_STAFF)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'entreprise')

    def __str__(self):
        return f"{self.user.username} @ {self.entreprise} ({self.role})"
    
    def can_manage_members(self) -> bool:
        return self.role == self.ROLE_ADMIN

    def can_edit_data(self) -> bool:
        return self.role in (self.ROLE_ADMIN, self.ROLE_STAFF)
