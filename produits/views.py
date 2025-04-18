from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Produit
from .forms import ProduitForm
from django.contrib import messages
from django.core.paginator import Paginator

def produit_list(request):
    produits_list = Produit.objects.all().order_by('nom')
    paginator = Paginator(produits_list, 8)
    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)
    return render(request, 'produits/produit_list.html', {'produits': produits})

def produit_create(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit ajouté avec succès.')
            return redirect('produit_list')
    else:
        form = ProduitForm()
    return render(request, 'produits/produit_form.html', {'form': form})

def produit_create_ajax(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            produit = form.save()
            return JsonResponse({'success': True, 'id': produit.id, 'nom': produit.nom})
        return JsonResponse({'success': False, 'error': form.errors.as_json()})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def get_prix_produit(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)
        return JsonResponse({'prix_unitaire': float(produit.prix_unitaire)})
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)
    
def produit_update(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit modifié avec succès.')
            return redirect('produit_list')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'produits/produit_form.html', {'form': form})

def produit_delete(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, 'Produit supprimé avec succès.')
        return redirect('produit_list')
    return render(request, 'produits/produit_confirm_delete.html', {'produit': produit})