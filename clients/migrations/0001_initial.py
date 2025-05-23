# Generated by Django 5.2 on 2025-04-17 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('adresse', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
