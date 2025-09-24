# factures/views.py
import json
import os
from django.conf import settings  # <-- AJOUT PDF
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # <-- AJOUT
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, IntegrityError  # <-- AJOUT IntegrityError
from django.db.models import OuterRef, Subquery, Exists  # <-- Annotations proformas
from django.http import HttpResponse  # <-- AJOUT PDF
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string  # <-- AJOUT PDF
from django.utils import timezone
from django.views.decorators.http import require_POST  # <-- AJOUT

import pdfkit  # <-- AJOUT PDF

from .forms import FactureForm, LigneFactureForm
from .models import Facture, LigneFacture
from .utils import generer_numero, montant_en_lettres  # <-- AJOUT si tu l’as mis dans utils
from clients.models import Client
from produits.models import Produit
from django.forms import formset_factory, inlineformset_factory


# (Optionnel) helper pour créer un inlineformset, si tu veux le réutiliser
def _get_formset():
    return inlineformset_factory(
        Facture,
        LigneFacture,
        form=LigneFactureForm,
        extra=1,
        can_delete=True
    )


# (Optionnel) Helper : récupérer la facture liée à une proforma
def _get_facture_cible(proforma):
    """Essaie d’obtenir la facture liée à cette proforma, quel que soit le reverse."""
    try:
        f = getattr(proforma, 'facture_cible', None)
        if f:
            return f
    except Facture.DoesNotExist:
        pass

    for attr in ('facture_cible_set', 'factures_cible', 'facture_set'):
        rel = getattr(proforma, attr, None)
        if hasattr(rel, 'all'):
            obj = rel.all().first()
            if obj:
                return obj

    return Facture.objects.filter(source_proforma=proforma).first()


# ----------------------
# LISTES
# ----------------------
@login_required
def liste_factures(request):
    ent = request.entreprise  # <-- multi-entreprise
    qs = (Facture.objects
          .select_related('client')
          .filter(entreprise=ent, type_document='facture')  # <-- filtre
          .order_by('-date', '-id'))

    paginator = Paginator(qs, 10)   # 10 factures/page
    factures_page = paginator.get_page(request.GET.get('page'))

    # ⚠️ Le template doit boucler sur 'factures'
    return render(request, 'factures/liste_factures.html', {
        'factures': factures_page,
    })


@login_required
def liste_proformas(request):
    ent = request.entreprise

    latest_facture_id = (
        Facture.objects
        .filter(entreprise=ent, type_document='facture', source_proforma=OuterRef('pk'))
        .order_by('-id')
        .values('id')[:1]
    )

    any_facture_exists = Facture.objects.filter(
        entreprise=ent,
        type_document='facture',
        source_proforma=OuterRef('pk')
    )

    qs = (
        Facture.objects
        .filter(entreprise=ent, type_document='proforma')
        .annotate(
            facture_cible_id=Subquery(latest_facture_id),
            deja_convertie=Exists(any_facture_exists),
        )
        .select_related('client')
        .order_by('-date', '-id')
    )

    paginator = Paginator(qs, 10)
    proformas_page = paginator.get_page(request.GET.get('page'))

    # ⚠️ Le template doit boucler sur 'proformas'
    return render(request, 'factures/liste_proformas.html', {
        'proformas': proformas_page,
    })


# ----------------------
# DETAIL
# ----------------------
@login_required
def detail_facture(request, pk):
    ent = request.entreprise
    facture = get_object_or_404(Facture, pk=pk, entreprise=ent)  # <-- filtre entreprise
    return render(request, 'factures/detail_facture.html', {'facture': facture})



@login_required
@transaction.atomic
def ajouter_facture(request):
    ent = request.entreprise

    # Formset libre (page d'ajout)
    LigneFormSet = formset_factory(LigneFactureForm, extra=1, can_delete=True)

    # Pour l'auto-remplissage JS des prix
    produits = Produit.objects.filter(entreprise=ent)
    prix_dict = {str(p.id): float(p.prix_unitaire) for p in produits}

    if request.method == 'POST':
        # 🔹 On passe l'entreprise au formulaire (filtre les clients)
        facture_form = FactureForm(request.POST, entreprise=ent)

        # 🔹 Et au formset (filtre les produits)
        formset = LigneFormSet(
            request.POST,
            prefix='lignes',
            form_kwargs={'entreprise': ent}
        )

        if facture_form.is_valid() and formset.is_valid():
            facture = facture_form.save(commit=False)
            facture.entreprise = ent

            # Numéro si absent → série entreprise + type
            if not facture.numero:
                facture.numero = generer_numero(ent, facture.type_document)

            # Sauvegarde résiliente (collision UNIQUE exceptionnelle)
            tries, saved = 0, False
            while not saved and tries < 5:
                try:
                    facture.save()
                    saved = True
                except IntegrityError:
                    tries += 1
                    facture.numero = generer_numero(ent, facture.type_document)

            if not saved:
                messages.error(request, "Impossible de générer un numéro unique. Réessayez.")
                return render(request, 'factures/ajouter_facture.html', {
                    'facture_form': facture_form,
                    'formset': formset,
                    'prix_json': json.dumps(prix_dict, cls=DjangoJSONEncoder),
                })

            # Lignes
            lignes_creees = 0
            for f in formset:
                if not f.cleaned_data or f.cleaned_data.get('DELETE'):
                    continue
                produit = f.cleaned_data.get('produit')
                quantite = f.cleaned_data.get('quantite')
                if produit and quantite:
                    LigneFacture.objects.create(
                        facture=facture,
                        produit=produit,
                        quantite=quantite,
                        prix_unitaire=f.cleaned_data.get('prix_unitaire') or produit.prix_unitaire,
                        remise_type=f.cleaned_data.get('remise_type') or 'aucune',
                        remise_valeur=f.cleaned_data.get('remise_valeur') or 0,
                    )
                    lignes_creees += 1

            if lignes_creees == 0:
                transaction.set_rollback(True)
                messages.error(request, "Veuillez saisir au moins une ligne.")
            else:
                messages.success(request, "Document enregistré avec succès.")
                return redirect('factures:liste_proformas' if facture.type_document == 'proforma' else 'factures:liste')
    else:
        facture_form = FactureForm(entreprise=ent)  # <-- filtre client sur l'entreprise
        formset = LigneFormSet(prefix='lignes', form_kwargs={'entreprise': ent})  # <-- filtre produits

    return render(request, 'factures/ajouter_facture.html', {
        'facture_form': facture_form,
        'formset': formset,
        'prix_json': json.dumps(prix_dict, cls=DjangoJSONEncoder),
    })


@login_required
@transaction.atomic
def modifier_facture(request, pk):
    ent = request.entreprise
    facture = get_object_or_404(Facture, pk=pk, entreprise=ent)

    # Inline formset lié à l'instance
    LigneInlineFormSet = inlineformset_factory(
        Facture, LigneFacture,
        form=LigneFactureForm,
        extra=0,
        can_delete=True
    )

    # Auto-remplissage JS (facultatif)
    produits = Produit.objects.filter(entreprise=ent)
    prix_dict = {str(p.id): float(p.prix_unitaire) for p in produits}

    old_type = facture.type_document

    if request.method == 'POST':
        # 🔹 On passe l'entreprise pour filtrer client & produits
        facture_form = FactureForm(request.POST, instance=facture, entreprise=ent)
        formset = LigneInlineFormSet(
            request.POST,
            instance=facture,
            form_kwargs={'entreprise': ent}
        )

        if facture_form.is_valid() and formset.is_valid():
            mod = facture_form.save(commit=False)
            mod.entreprise = ent

            # Si changement de type → renumérotation dans la série *du nouveau type*
            if old_type != mod.type_document:
                mod.numero = generer_numero(ent, mod.type_document)

            # Sauvegarde résiliente
            tries, saved = 0, False
            while not saved and tries < 5:
                try:
                    mod.save()
                    saved = True
                except IntegrityError:
                    tries += 1
                    mod.numero = generer_numero(ent, mod.type_document)

            if not saved:
                messages.error(request, "Impossible de générer un numéro unique.")
                return render(request, 'factures/modifier_facture.html', {
                    'facture_form': facture_form,
                    'formset': formset,
                    'prix_json': json.dumps(prix_dict, cls=DjangoJSONEncoder),
                    'facture': facture,
                })

            formset.save()
            messages.success(request, "Document modifié avec succès.")
            return redirect('factures:detail', pk=mod.pk)

    else:
        facture_form = FactureForm(instance=facture, entreprise=ent)
        formset = LigneInlineFormSet(instance=facture, form_kwargs={'entreprise': ent})

    return render(request, 'factures/modifier_facture.html', {
        'facture_form': facture_form,
        'formset': formset,
        'prix_json': json.dumps(prix_dict, cls=DjangoJSONEncoder),
        'facture': facture,
    })


# ----------------------
# CONVERTIR PROFORMA -> FACTURE
# ----------------------
@login_required
@require_POST
@transaction.atomic
def convertir_proforma(request, pk):
    ent = request.entreprise
    proforma = get_object_or_404(Facture, pk=pk, entreprise=ent, type_document='proforma')

    # Déjà convertie ?
    exist = (Facture.objects
             .filter(entreprise=ent, type_document='facture', source_proforma=proforma)
             .order_by('-id')
             .first())
    if exist:
        messages.info(request, f"Déjà convertie en {exist.numero}.")
        return redirect('factures:detail', pk=exist.pk)

    # Convertir
    numero = generer_numero(ent, 'facture')
    facture = Facture.objects.create(
        entreprise=ent,
        type_document='facture',
        client=proforma.client,
        statut='brouillon',
        objet=proforma.objet,
        tva=proforma.tva,
        remise_globale_type=proforma.remise_globale_type,
        remise_globale_valeur=proforma.remise_globale_valeur,
        frais_livraison=proforma.frais_livraison,
        numero=numero,
        source_proforma=proforma,
        date=timezone.now().date(),
    )

    for l in proforma.lignes.all():
        LigneFacture.objects.create(
            facture=facture,
            produit=l.produit,
            quantite=l.quantite,
            prix_unitaire=l.prix_unitaire,
            remise_type=l.remise_type,
            remise_valeur=l.remise_valeur,
        )

    proforma.statut = 'convertie'
    proforma.save(update_fields=['statut'])

    messages.success(request, f"Proforma convertie en facture {facture.numero}.")
    return redirect('factures:detail', pk=facture.pk)

# ----------------------
# SUPPRIMER
# ----------------------
@login_required
@transaction.atomic
def supprimer_facture(request, pk):
    ent = request.entreprise
    facture = get_object_or_404(Facture, pk=pk, entreprise=ent)
    if request.method == 'POST':
        type_doc = facture.type_document
        facture.delete()
        messages.success(request, "Document supprimé.")
        return redirect('factures:liste_proformas' if type_doc == 'proforma' else 'factures:liste')
    return render(request, 'factures/supprimer_facture.html', {'facture': facture})


# ----------------------
# PDF (wkhtmltopdf)
# ----------------------
@login_required
def document_pdf(request, pk):
    """Génère le PDF de facture/proforma via wkhtmltopdf."""
    ent = request.entreprise
    doc = get_object_or_404(Facture, pk=pk, entreprise=ent)
    ttc = doc.total_ttc()
    logo_path = None

    if ent and getattr(ent, 'logo', None):
        # wkhtmltopdf → préférer file:/// chemin absolu local
        p = ent.logo.path  # nécessite Pillow & MEDIA_ROOT correct
        if os.path.exists(p):
            logo_path = 'file:///' + p.replace('\\', '/')

    html = render_to_string('factures/pdf_document.html', {
        'doc': doc,
        'is_proforma': (doc.type_document == 'proforma'),
        'request': request,
        'entreprise': ent,  
        'logo_path': logo_path,
        'montant_lettres': montant_en_lettres(ttc),  # <-- util (mets-le dans utils si pas encore)
    })

    options = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '12mm',
        'margin-left': '10mm',
        'encoding': "UTF-8",
        'enable-local-file-access': None,  # nécessaire sous Windows
    }

    config = pdfkit.configuration(wkhtmltopdf=getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf'))
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    filename = f"{'PROFORMA' if doc.type_document=='proforma' else 'FACTURE'}_{(doc.numero or doc.pk)}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@login_required
def bordereau_livraison(request, pk):
    ent = request.entreprise
    facture = get_object_or_404(Facture, pk=pk, entreprise=ent)
    lignes = facture.lignes.all()

    # Logo entreprise (comme pour les factures)
    logo_path = None
    if ent and getattr(ent, 'logo', None):
        p = ent.logo.path
        if os.path.exists(p):
            logo_path = 'file:///' + p.replace('\\', '/')

    # Rendu HTML du template bordereau
    html = render_to_string('factures/bordereau_livraison.html', {
        'facture': facture,
        'lignes': lignes,
        'entreprise': ent,
        'logo_path': logo_path,
        'request': request,
    })

    # Options PDF
    options = {
        'page-size': 'A4',
        'margin-top': '10mm',
        'margin-right': '10mm',
        'margin-bottom': '12mm',
        'margin-left': '10mm',
        'encoding': "UTF-8",
        'enable-local-file-access': None,  # important pour que wkhtmltopdf lise les images locales
    }

    # Génération PDF
    config = pdfkit.configuration(wkhtmltopdf=getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf'))
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    filename = f"BDL_{facture.numero or facture.pk}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
