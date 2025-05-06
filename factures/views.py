from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.http import Http404
from .models import Facture, LigneFacture
from .forms import FactureForm, FactureLigneFormSet, LigneFactureForm, FactureLigneFormSetConversion
from django.contrib import messages
from django.core.paginator import Paginator
import logging
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_weasyprint import WeasyTemplateResponseMixin
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO

def facture_list(request):
    factures_list = Facture.objects.filter(type_facture='facture').order_by('-date')
    paginator = Paginator(factures_list, 10)
    page_number = request.GET.get('page')
    factures = paginator.get_page(page_number)
    return render(request, 'factures/facture_list.html', {'factures': factures})

def proforma_list(request):
    proformas_list = Facture.objects.filter(type_facture='proforma').order_by('-date')
    paginator = Paginator(proformas_list, 10)
    page_number = request.GET.get('page')
    proformas = paginator.get_page(page_number)
    return render(request, 'factures/proforma_list.html', {'proformas': proformas})

def facture_create(request):
    LigneFactureFormSet = modelformset_factory(
        LigneFacture, form=LigneFactureForm, extra=2, can_delete=True
    )
    if request.method == 'POST':
        form = FactureForm(request.POST)
        formset = LigneFactureFormSet(request.POST, queryset=LigneFacture.objects.none())
        if form.is_valid() and formset.is_valid():
            facture = form.save()
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    ligne = form.save(commit=False)
                    ligne.facture = facture
                    ligne.save()
            messages.success(request, f'Facture {facture.numero} créée avec succès.')
            return redirect('facture_list')
        else:
            messages.error(request, "Erreur lors de la création de la facture.")
            if not form.is_valid():
                messages.error(request, f"Erreurs dans le formulaire principal : {form.errors}")
            if not formset.is_valid():
                messages.error(request, f"Erreurs dans les lignes de facture : {formset.errors}")
    else:
        form = FactureForm()
        formset = LigneFactureFormSet(queryset=LigneFacture.objects.none())
    return render(request, 'factures/facture_form.html', {
        'form': form,
        'formset': formset,
    })

def facture_detail(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    return render(request, 'factures/facture_detail.html', {'facture': facture})


def facture_update(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)
        formset = FactureLigneFormSet(request.POST, instance=facture)
        logger.debug(f"Données POST: {request.POST}")
        if form.is_valid():
            logger.debug("Formulaire FactureForm valide")
        else:
            logger.debug(f"Erreurs FactureForm: {form.errors}")
        if formset.is_valid():
            logger.debug("Formset FactureLigneFormSet valide")
            logger.debug(f"Données formset nettoyées: {[form.cleaned_data for form in formset]}")
        else:
            logger.debug(f"Erreurs Formset: {formset.errors}")
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            logger.debug(f"Facture mise à jour: ID={facture.id}")
            logger.debug(f"Lignes de facture sauvegardées: {facture.lignefacture_set.all()}")
            return redirect('facture_list')
        else:
            logger.error(f"Erreur lors de la modification de la facture. Erreurs form: {form.errors}, Erreurs formset: {formset.errors}")
    else:
        form = FactureForm(instance=facture)
        formset = FactureLigneFormSet(instance=facture)
    
    return render(request, 'factures/facture_update.html', {
        'form': form,
        'formset': formset,
        'facture': facture,
    })


logger = logging.getLogger(__name__)

def proforma_to_facture(request, pk):
    proforma = get_object_or_404(Facture, id=pk, type_facture='proforma')
    
    # Loguer les lignes du proforma
    lignes = proforma.lignefacture_set.all()
    logger.debug(f"Lignes du proforma ID={pk}: {list(lignes)}")
    
    if request.method == 'POST':
        form = FactureForm(request.POST)
        # Initialiser le formset sans instance
        formset = FactureLigneFormSetConversion(request.POST)
        logger.debug(f"Données POST: {request.POST}")
        if form.is_valid():
            logger.debug("Formulaire FactureForm valide")
        else:
            logger.debug(f"Erreurs FactureForm: {form.errors}")
        if formset.is_valid():
            logger.debug("Formset FactureLigneFormSetConversion valide")
            logger.debug(f"Données formset nettoyées: {[form.cleaned_data for form in formset]}")
        else:
            logger.debug(f"Erreurs Formset: {formset.errors}")
        if form.is_valid() and formset.is_valid():
            facture = form.save(commit=False)
            facture.type_facture = 'facture'
            facture.statut = 'brouillon'
            facture.save()
            logger.debug(f"Facture créée: ID={facture.id}")
            
            # Créer de nouvelles lignes explicitement
            for form in formset:
                if not form.cleaned_data.get('DELETE', False):
                    LigneFacture.objects.create(
                        facture=facture,
                        produit=form.cleaned_data['produit'],
                        quantite=form.cleaned_data['quantite'],
                        prix_unitaire=form.cleaned_data['prix_unitaire']
                    )
            logger.debug(f"Lignes de facture sauvegardées: {facture.lignefacture_set.all()}")
            
            proforma.statut = 'converti'
            proforma.save()
            logger.debug("Proforma marqué comme converti")
            return redirect('facture_list')
    else:
        form = FactureForm(initial={
            'client': proforma.client,
            'type_facture': 'facture',
            'statut': 'brouillon',
            'remise_globale_type': proforma.remise_globale_type,
            'remise_globale_valeur': proforma.remise_globale_valeur,
            'frais_livraison': proforma.frais_livraison,
            'tva': proforma.tva,
        })
        initial_data = [
            {
                'produit': ligne.produit.id,
                'quantite': ligne.quantite,
                'prix_unitaire': ligne.prix_unitaire,
            } for ligne in proforma.lignefacture_set.all()
        ]
        logger.debug(f"Données initiales du formset: {initial_data}")
        formset = FactureLigneFormSetConversion(
            instance=proforma,
            initial=initial_data,
            queryset=lignes
        )
    
    return render(request, 'factures/facture_convert.html', {
        'form': form,
        'formset': formset,
        'proforma': proforma,
    })

def facture_delete(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, 'Facture supprimée avec succès.')
        return redirect('facture_list')
    return render(request, 'factures/facture_confirm_delete.html', {'facture': facture})

class FacturePDFView(WeasyTemplateResponseMixin, DetailView):
    model = Facture
    template_name = 'factures/facture_pdf.html'
    context_object_name = 'facture'
    pdf_filename = 'facture_{id}.pdf'

    def get_pdf_filename(self):
        return self.pdf_filename.format(id=self.object.id)
    
    def facture_pdf_view(request, pk):
        facture = get_object_or_404(Facture, pk=pk)
        template = get_template('factures/facture_pdf.html')
        context = {'facture': facture}
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{pk}.pdf"'
        
        pdf = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
        if pdf.err:
            return HttpResponse('Erreur lors de la génération du PDF', status=500)
        return response