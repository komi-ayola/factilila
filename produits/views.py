# produits/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Produit
from .forms import ProduitForm


@login_required
def liste_produits(request):
    ent = request.entreprise
    qs = (Produit.objects
          .filter(entreprise=ent)
          .order_by('nom'))
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)

    return render(request, 'produits/liste_produits.html', {
        'produits': produits,   # <— le template boucle sur 'produits'
    })


@login_required
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.entreprise = request.entreprise   # <— ATTACHE à l’entreprise
            produit.save()                            # <— ✅ (et pas form.save())
            messages.success(request, "Produit ajouté avec succès.")
            return redirect('produits:liste')
    else:
        form = ProduitForm()

    return render(request, 'produits/ajouter_produit.html', {
        'form': form,
        'titre': "Nouveau produit",
    })


@login_required
def detail_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk, entreprise=request.entreprise)
    return render(request, 'produits/detail_produit.html', {'produit': produit})


@login_required
def modifier_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk, entreprise=request.entreprise)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.entreprise = request.entreprise  # sécurité si le champ n’est pas exposé
            obj.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect('produits:detail', pk=produit.pk)
    else:
        form = ProduitForm(instance=produit)

    return render(request, 'produits/modifier_produit.html', {
        'form': form,
        'titre': f"Modifier {produit.nom}",
        'produit': produit
    })


@login_required
def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk, entreprise=request.entreprise)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, "Produit supprimé.")
        return redirect('produits:liste')
    return render(request, 'produits/confirmer_suppression.html', {
        'objet': produit,
        'type_objet': 'produit'
    })
