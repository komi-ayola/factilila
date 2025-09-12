# entreprises/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm

from .models import Entreprise, MembreEntreprise

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@domaine.com'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Mot de passe"}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirmer le mot de passe"}),
        }


class EntrepriseForm(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = [
            'nom', 'nom_affichage', 'ville', 'pays',
            'telephone', 'email', 'adresse', 'logo', 'nom_signataire'
        ]
        labels = {
            'nom': "Nom légal",
            'nom_affichage': "Nom d'affichage (PDF)",
            'nom_signataire': "Nom du signataire",
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_affichage': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nom_signataire': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MemberAddForm(forms.Form):
    user_identifier = forms.CharField(
        label="Utilisateur (username ou email)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "ex: johndoe ou john@mail.com"})
    )
    role = forms.ChoiceField(
        label="Rôle",
        choices=MembreEntreprise.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        self.entreprise = kwargs.pop('entreprise', None)
        super().__init__(*args, **kwargs)

    def clean_user_identifier(self):
        ident = self.cleaned_data['user_identifier'].strip()
        try:
            if '@' in ident:
                user = User.objects.get(email__iexact=ident)
            else:
                user = User.objects.get(username__iexact=ident)
        except User.DoesNotExist:
            raise forms.ValidationError(
                "Aucun utilisateur avec cet identifiant. (Pour l’instant, on ne peut ajouter que des comptes existants.)"
            )
        if MembreEntreprise.objects.filter(user=user, entreprise=self.entreprise).exists():
            raise forms.ValidationError("Cet utilisateur est déjà membre de l’entreprise.")
        self.cleaned_user = user
        return ident

    def save(self):
        return MembreEntreprise.objects.create(
            user=self.cleaned_user,
            entreprise=self.entreprise,
            role=self.cleaned_data['role']
        )


class MemberRoleForm(forms.ModelForm):
    class Meta:
        model = MembreEntreprise
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


#  Création d’un compte utilisateur + ajout direct comme membre ---
class MemberCreateForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "ex: odette"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "ex: odette@mail.com"})
    )
    role = forms.ChoiceField(
        label="Rôle",
        choices=MembreEntreprise.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    send_email = forms.BooleanField(
        required=False,
        initial=True,
        label="Envoyer par email le mot de passe temporaire",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        self.entreprise = kwargs.pop('entreprise', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d’utilisateur existe déjà.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email


class InvitePasswordResetForm(PasswordResetForm):
    """
    Variante de PasswordResetForm qui inclut AUSSI les utilisateurs
    ayant un mot de passe inutilisable (set_unusable_password),
    utile pour le flux d'invitation.
    """
    def get_users(self, email):
        # Utilisateurs actifs avec cet email (sans filtrer has_usable_password)
        active_users = User._default_manager.filter(
            email__iexact=email,
            is_active=True,
        )
        return (u for u in active_users if u.email)
