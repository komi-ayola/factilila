from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Client
from .forms import ClientForm
from django.contrib import messages
from django.core.paginator import Paginator

def client_list(request):
    clients_list = Client.objects.all().order_by('nom')
    paginator = Paginator(clients_list, 10)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    return render(request, 'clients/client_list.html', {'clients': clients})

def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client ajouté avec succès.')
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'clients/client_form.html', {'form': form})

def client_create_ajax(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            return JsonResponse({'success': True, 'id': client.id, 'nom': client.nom})
        return JsonResponse({'success': False, 'error': form.errors.as_json()})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def client_update(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client modifié avec succès.')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form})

def client_delete(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Client supprimé avec succès.')
        return redirect('client_list')
    return render(request, 'clients/client_confirm_delete.html', {'client': client})
