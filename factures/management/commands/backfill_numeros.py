from django.core.management.base import BaseCommand
from django.db import transaction
from factures.models import Facture
from factures.views import generer_numero_facture  # ou recopie la fonction ici si tu préfères

class Command(BaseCommand):
    help = "Assigne un numéro aux factures/proformas qui n'en ont pas encore."

    @transaction.atomic
    def handle(self, *args, **options):
        total = 0

        # Documents sans numéro (vide ou null)
        qs = Facture.objects.filter(numero__isnull=True) | Facture.objects.filter(numero='')
        qs = qs.select_related('client').order_by('date', 'id')

        for f in qs:
            numero = generer_numero_facture(f.type_document)
            # S'il existe déjà par collision improbable, on régénère (boucle de sûreté)
            while Facture.objects.filter(numero=numero).exists():
                numero = generer_numero_facture(f.type_document)
            f.numero = numero
            f.save(update_fields=['numero'])
            total += 1
            self.stdout.write(self.style.SUCCESS(f"[OK] {f.id} -> {f.numero} ({f.get_type_document_display()})"))

        self.stdout.write(self.style.WARNING(f"Terminé. {total} document(s) mis à jour."))
