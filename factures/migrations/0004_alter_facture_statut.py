# Generated by Django 5.2 on 2025-04-18 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0003_alter_facture_tva'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='statut',
            field=models.CharField(choices=[('brouillon', 'Brouillon'), ('envoyee', 'Envoyée'), ('payee', 'Payée'), ('annulee', 'Annulée'), ('converti', 'Converti')], default='brouillon', max_length=10),
        ),
    ]
