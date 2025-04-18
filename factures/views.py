from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.http import Http404
from .models import Facture, LigneFacture
from .forms import FactureForm, LigneFactureForm
from django.contrib import messages
from django.core.paginator import Paginator

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
    LigneFactureFormSet = modelformset_factory(
        LigneFacture, form=LigneFactureForm, extra=1, can_delete=True
    )
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)
        formset = LigneFactureFormSet(request.POST, queryset=facture.lignefacture_set.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            for form in formset:
                if form.cleaned_data:
                    if form.cleaned_data.get('DELETE', False):
                        if form.instance.pk:
                            form.instance.delete()
                    else:
                        ligne = form.save(commit=False)
                        ligne.facture = facture
                        ligne.save()
            messages.success(request, f'Facture {facture.numero} modifiée avec succès.')
            return redirect('facture_list')
        else:
            messages.error(request, "Erreur lors de la modification de la facture.")
            if not form.is_valid():
                messages.error(request, f"Erreurs dans le formulaire principal : {form.errors}")
            if not formset.is_valid():
                messages.error(request, f"Erreurs dans les lignes de facture : {formset.errors}")
    else:
        form = FactureForm(instance=facture)
        formset = LigneFactureFormSet(queryset=facture.lignefacture_set.all())
    return render(request, 'factures/facture_update.html', {
        'form': form,
        'formset': formset,
        'facture': facture,
    })

def proforma_to_facture(request, pk):
    proforma = get_object_or_404(Facture, pk=pk, type_facture='proforma')
    LigneFactureFormSet = modelformset_factory(
        LigneFacture, form=LigneFactureForm, extra=1, can_delete=True
    )
    if request.method == 'POST':
        form = FactureForm(request.POST)
        formset = LigneFactureFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            facture = form.save(commit=False)
            facture.type_facture = 'facture'
            facture.statut = 'brouillon'
            facture.save()
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    ligne = form.save(commit=False)
                    ligne.facture = facture
                    ligne.save()
            proforma.statut = 'converti'
            proforma.save()
            messages.success(request, f'Proforma {proforma.numero} converti en facture {facture.numero} avec succès.')
            return redirect('facture_list')
        else:
            messages.error(request, "Erreur lors de la conversion du proforma.")
            if not form.is_valid():
                messages.error(request, f"Erreurs dans le formulaire principal : {form.errors}")
            if not formset.is_valid():
                messages.error(request, f"Erreurs dans les lignes de facture : {formset.errors}")
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
        formset = LigneFactureFormSet(queryset=proforma.lignefacture_set.all())
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