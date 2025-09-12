from django.db import migrations

def backfill_client_entreprise(apps, schema_editor):
    Client = apps.get_model('clients', 'Client')
    Facture = apps.get_model('factures', 'Facture')
    Entreprise = apps.get_model('entreprises', 'Entreprise')
    Produit =apps.get_model('produits', 'Produit')

    # Entreprise par défaut si besoin
    ent = Entreprise.objects.first()
    if ent is None:
        ent = Entreprise.objects.create(
            nom="LILA'S",
            nom_affichage="LILA'S",
            ville="Lomé",
            pays="Togo",
            telephone="+228 91 91 27 15/97 82 00 29",
            email="societelilas@gmail.com",
        )

    for c in Client.objects.filter(entreprise__isnull=True):
        # Essaie de déduire l’entreprise via une facture de ce client
        f = Facture.objects.filter(client=c).order_by('id').first()
        if f and getattr(f, 'entreprise_id', None):
            c.entreprise_id = f.entreprise_id
        else:
            c.entreprise = ent
        c.save(update_fields=['entreprise'])

class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_alter_client_entreprise'),
        ('factures', '0009_alter_facture_entreprise'),
        ('produits', '0004_alter_produit_entreprise'),
        ('entreprises', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_client_entreprise, migrations.RunPython.noop),
    ]
