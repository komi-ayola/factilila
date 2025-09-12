# entreprises/views.py
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string

from .forms import SignupForm, EntrepriseForm, MemberAddForm, MemberRoleForm, MemberCreateForm
from .models import Entreprise, MembreEntreprise
from .permissions import require_manage_members, require_member
from django.views.decorators.http import require_POST

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Entreprise.objects.create(
                proprietaire=user,
                nom=user.username,
                nom_affichage=user.username,
                pays="Togo",
            )
            login(request, user)
            return redirect('entreprises:profil')
    else:
        form = SignupForm()
    return render(request, 'entreprises/signup.html', {'form': form})


@login_required
def profil_entreprise(request):
    ent = Entreprise.objects.filter(proprietaire=request.user).first()
    if not ent:
        messages.info(request, "Aucune entreprise liée à votre compte. Créez-en une.")
        return redirect('entreprises:signup')

    if request.method == 'POST':
        form = EntrepriseForm(request.POST, request.FILES, instance=ent)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil entreprise mis à jour.")
            return redirect('entreprises:profil')
    else:
        form = EntrepriseForm(instance=ent)

    return render(request, 'entreprises/profil.html', {'form': form, 'entreprise': ent})


@login_required
@require_member
def switch_entreprise(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Méthode invalide.")
    ent_id = request.POST.get('entreprise_id')
    if not ent_id:
        return HttpResponseBadRequest("ID manquant.")

    can_access = (Entreprise.objects
                  .filter(
                      Q(id=ent_id) & (
                          Q(proprietaire=request.user) |
                          Q(membreentreprise__user=request.user, membreentreprise__is_active=True)
                      )
                  )
                  .exists())
    if not can_access:
        messages.error(request, "Vous n’avez pas accès à cette entreprise.")
        return redirect('core:home')

    request.session['active_entreprise_id'] = int(ent_id)
    messages.success(request, "Entreprise active modifiée.")
    return redirect(request.POST.get('next') or 'core:home')


# ====== GESTION DES MEMBRES ======

@login_required
@require_manage_members
def gestion_membres(request):
    ent = request.entreprise
    membres = (MembreEntreprise.objects
               .select_related('user')
               .filter(entreprise=ent)
               .order_by('user__username'))
    form_add = MemberAddForm(entreprise=ent)
    return render(request, 'entreprises/gestion_membres.html', {
        'entreprise': ent,
        'membres': membres,
        'form_add': form_add,
        'form_create': MemberCreateForm(entreprise=ent)
    })


@login_required
@require_manage_members
@require_POST
@transaction.atomic
def ajouter_membre(request):
    ent = request.entreprise
    if request.method != 'POST':
        return redirect('entreprises:gestion_membres')

    form_add = MemberAddForm(request.POST, entreprise=ent)
    if form_add.is_valid():
        form_add.save()
        messages.success(request, "Membre ajouté avec succès.")
        return redirect('entreprises:gestion_membres')

    membres = (MembreEntreprise.objects
               .select_related('user')
               .filter(entreprise=ent)
               .order_by('user__username'))
    return render(request, 'entreprises/gestion_membres.html', {
        'entreprise': ent,
        'membres': membres,
        'form_add': form_add,
    })


@login_required
@require_manage_members
@transaction.atomic
def changer_role(request, membre_id):
    ent = request.entreprise
    membre = get_object_or_404(MembreEntreprise, id=membre_id, entreprise=ent)

    if membre.user_id == ent.proprietaire_id:
        messages.error(request, "Impossible de modifier le rôle du propriétaire.")
        return redirect('entreprises:gestion_membres')

    if request.method != 'POST':
        return redirect('entreprises:gestion_membres')

    form = MemberRoleForm(request.POST, instance=membre)
    if form.is_valid():
        form.save()
        messages.success(request, "Rôle mis à jour.")
    else:
        messages.error(request, "Formulaire invalide.")
    return redirect('entreprises:gestion_membres')


@login_required
@require_manage_members
@transaction.atomic
def retirer_membre(request, membre_id):
    ent = request.entreprise
    membre = get_object_or_404(MembreEntreprise, id=membre_id, entreprise=ent)

    if membre.user_id == ent.proprietaire_id:
        messages.error(request, "Impossible de supprimer le propriétaire.")
        return redirect('entreprises:gestion_membres')

    # Empêcher de retirer le dernier admin
    if membre.role == MembreEntreprise.ROLE_ADMIN:
        admins = MembreEntreprise.objects.filter(entreprise=ent, role=MembreEntreprise.ROLE_ADMIN, is_active=True).count()
        if admins <= 1:
            messages.error(request, "Il doit rester au moins un administrateur.")
            return redirect('entreprises:gestion_membres')
        
    if request.method != 'POST':
        return redirect('entreprises:gestion_membres')
    

    membre.delete()
    messages.success(request, "Membre retiré.")
    return redirect('entreprises:gestion_membres')


# ====== NOUVEAU : Création d’un compte utilisateur + ajout direct à l’entreprise ======
@login_required
@require_manage_members
@transaction.atomic
def creer_utilisateur_membre(request):
    ent = request.entreprise
    if request.method == 'POST':
        form = MemberCreateForm(request.POST, entreprise=ent)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            send_email = form.cleaned_data['send_email']

            # Génère un mot de passe temporaire
            temp_password = get_random_string(10)

            # Crée l’utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=temp_password
            )

            # L’ajoute comme membre
            MembreEntreprise.objects.create(
                user=user,
                entreprise=ent,
                role=role
            )

            # Envoie un e-mail (si backend configuré)
            if send_email:
                try:
                    send_mail(
                        subject="Votre compte a été créé",
                        message=(
                            f"Bonjour {username},\n\n"
                            f"Un compte a été créé pour vous sur FactiLila pour l’entreprise « {ent.nom_affichage or ent.nom} ».\n"
                            f"Identifiants :\n"
                            f"  - Nom d’utilisateur : {username}\n"
                            f"  - Mot de passe temporaire : {temp_password}\n\n"
                            f"Veuillez vous connecter puis changer votre mot de passe.\n"
                        ),
                        from_email=None,  # Utilise DEFAULT_FROM_EMAIL si défini
                        recipient_list=[email],
                        fail_silently=True
                    )
                except Exception:
                    # On ne bloque pas le flux si l’envoi échoue
                    pass

            messages.success(request, f"Utilisateur « {username} » créé et ajouté comme membre.")
            return redirect('entreprises:gestion_membres')
    else:
        form = MemberCreateForm(entreprise=ent)

    return render(request, 'entreprises/creer_utilisateur_membre.html', {
        'entreprise': ent,
        'form': form
    })
