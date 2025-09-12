# entreprises/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entreprise, MembreEntreprise, MembreEntreprise as ME

@receiver(post_save, sender=Entreprise)
def add_owner_as_admin(sender, instance, created, **kwargs):
    if created and instance.proprietaire_id:
        MembreEntreprise.objects.get_or_create(
            user=instance.proprietaire,
            entreprise=instance,
            defaults={'role': ME.ROLE_ADMIN}
        )
