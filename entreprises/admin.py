# entreprises/admin.py
from django.contrib import admin
from .models import Entreprise

@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'nom_affichage', 'ville', 'pays', 'telephone', 'owner')
    search_fields = (
        'nom', 'nom_affichage', 'ville', 'pays', 'telephone',
        'proprietaire__username', 'proprietaire__email'
    )
    list_filter = ('pays', 'ville')
    readonly_fields = ('date_creation',)

    @admin.display(description="Propriétaire")
    def owner(self, obj):
        return obj.proprietaire.username if obj.proprietaire else "—"
