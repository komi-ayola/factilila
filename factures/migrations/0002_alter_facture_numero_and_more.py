# Generated by Django 5.2 on 2025-04-17 08:04

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='numero',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='facture',
            name='remise_globale_type',
            field=models.CharField(choices=[('aucune', 'Aucune'), ('pourcentage', 'Pourcentage'), ('montant_fixe', 'Montant fixe')], default='aucune', max_length=20),
        ),
        migrations.AlterField(
            model_name='facture',
            name='statut',
            field=models.CharField(choices=[('brouillon', 'Brouillon'), ('envoyee', 'Envoyée'), ('payee', 'Payée'), ('annulee', 'Annulée')], default='brouillon', max_length=10),
        ),
        migrations.AlterField(
            model_name='facture',
            name='type_facture',
            field=models.CharField(choices=[('facture', 'Facture'), ('proforma', 'Proforma')], default='facture', max_length=10),
        ),
        migrations.AlterField(
            model_name='lignefacture',
            name='facture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='factures.facture'),
        ),
        migrations.AlterField(
            model_name='lignefacture',
            name='quantite',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='lignefacture',
            name='remise_type',
            field=models.CharField(choices=[('aucune', 'Aucune'), ('pourcentage', 'Pourcentage'), ('montant_fixe', 'Montant fixe')], default='aucune', max_length=20),
        ),
        migrations.CreateModel(
            name='CompteurFacture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annee', models.IntegerField()),
                ('type_facture', models.CharField(choices=[('facture', 'Facture'), ('proforma', 'Proforma')], max_length=10)),
                ('dernier_numero', models.IntegerField(default=0)),
            ],
            options={
                'unique_together': {('annee', 'type_facture')},
            },
        ),
    ]
