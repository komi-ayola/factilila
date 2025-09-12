# clients/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Client
from .forms import ClientForm


@login_required
def liste_clients(request):
    ent = request.entreprise
    qs = (Client.objects
          .filter(entreprise=ent)
          .order_by('nom'))
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    return render(request, 'clients/liste_clients.html', {'clients': clients})


@login_required
def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.entreprise = request.entreprise
            client.save()
            messages.success(request, "Client ajouté avec succès.")
            return redirect('clients:liste')
    else:
        form = ClientForm()
    return render(request, 'clients/ajouter_client.html', {
        'form': form,
        'titre': "Nouveau client"
    })


@login_required
def detail_client(request, pk):
    client = get_object_or_404(Client, pk=pk, entreprise=request.entreprise)
    return render(request, 'clients/detail_client.html', {'client': client})


@login_required
def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk, entreprise=request.entreprise)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.entreprise = request.entreprise  # sécurité
            obj.save()
            messages.success(request, "Client modifié avec succès.")
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/ajouter_client.html', {
        'form': form,
        'titre': f"Modifier {client.nom}"
    })


@login_required
def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk, entreprise=request.entreprise)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé.")
        return redirect('clients:liste')
    return render(request, 'clients/confirmer_suppression.html', {
        'objet': client,
        'type_objet': 'client'
    })
