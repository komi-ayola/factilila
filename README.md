# Factilila – Système de Facturation Multi-Entreprise

Factilila est une application web complète de **gestion de facturation et de membres** développée avec **Django 5**.  
Elle permet de gérer plusieurs entreprises, d’ajouter des membres avec des rôles précis, et de générer des factures/proformas au format PDF.

---

## ✨ Fonctionnalités principales

### 💼 Gestion d’entreprise
- Création et mise à jour d’une ou plusieurs **entreprises**.
- Chaque entreprise a ses **propres clients, produits, factures et catégories**.
- Possibilité de changer d’entreprise active directement dans l’interface.

### 👥 Gestion des membres et rôles
- **Propriétaire** : super-administrateur de l’entreprise.
- **Administrateur** : gère l’équipe, les factures, les produits, les clients.
- **Staff** : peut créer et gérer les factures/clients/produits mais pas les membres.
- **Lecture seule** : accès en consultation uniquement.

> ✅ Le propriétaire peut inviter un membre existant ou **créer un nouvel utilisateur directement depuis l’interface**.  
> ✅ Un e-mail de réinitialisation/activation est envoyé au nouveau membre (ou un mot de passe temporaire est défini).

### 🧾 Gestion de facturation
- Création et modification de **factures** ou **proformas**.
- Gestion des **clients** et des **produits** propres à chaque entreprise.
- Ajout de **lignes de factures** (produits, quantités, prix unitaires).
- Calcul automatique des totaux : **HT, TVA, TTC**, avec **frais de livraison**.
- Génération de factures ou proformas **PDF personnalisées** avec logo.
- Conversion automatique des montants en lettres (par exemple :  
  *sept cent huit mille francs CFA*).

---

## ⚙️ Prérequis

- Python 3.12 ou supérieur  
- pip (gestionnaire de packages Python)  
- virtualenv (recommandé)  
- Git  
- [WeasyPrint](https://weasyprint.org/) (pour la génération de PDF)  
  > Sous Windows, installer GTK+ est requis.

---

## 🚀 Installation

1️⃣ **Cloner le dépôt**  
```bash
git clone https://github.com/komi-ayola/factilila.git
cd factilila
```

2️⃣ **Créer un environnement virtuel (recommandé)**  
```bash
python -m venv env
# Sur Windows :
env\Scripts\activate
```

3️⃣ **Installer les dépendances**  
Vérifiez que `requirements.txt` contient au moins :  
```
Django==5.1
django-weasyprint==2.2.1
weasyprint==62.3
```
Puis exécutez :
```bash
pip install -r requirements.txt
```

4️⃣ **Configurer WeasyPrint**  
- Installer [GTK+](https://weasyprint.readthedocs.io/en/latest/install.html#windows) si nécessaire.
- Vérifier le bon fonctionnement avec :  
```bash
python -c "import weasyprint; print(weasyprint.__version__)"
```

5️⃣ **Initialiser la base de données**  
```bash
python manage.py makemigrations
python manage.py migrate
```

6️⃣ **Créer un superutilisateur (facultatif)**  
```bash
python manage.py createsuperuser
```

---

## ▶️ Lancer l’application

Démarrer le serveur de développement :
```bash
python manage.py runserver
```

Puis accéder à :
- Application : http://127.0.0.1:8000/
- Administration Django : http://127.0.0.1:8000/admin/

---

## 💡 Utilisation

### Gestion des membres
- Menu **Entreprise → Gestion des membres**
- Ajouter un utilisateur existant (par son nom d’utilisateur ou email)
- OU créer un nouvel utilisateur directement depuis l’interface
- Modifier le rôle (Propriétaire, Admin, Staff, Lecture seule)
- Retirer un membre si nécessaire

### Création d’une facture
- Menu **Factures → Nouvelle facture**
- Sélectionner un client (ou en créer un nouveau)
- Ajouter les produits/lignes
- Générer le **PDF personnalisé** (facture ou proforma)

---

## 🤝 Contribution

Les contributions sont les bienvenues !  
Pour contribuer :
```bash
git checkout -b feature/ma-fonctionnalite
# ...faire vos changements...
git commit -m "Ajout de ma fonctionnalité"
git push origin feature/ma-fonctionnalite
```
Puis ouvrez une **Pull Request**.

---

## 📜 Licence
Projet sous licence MIT – voir le fichier `LICENSE`.

---

## 📬 Contact
Développé par **Komi Maza-Balo T. AYOLA**  
- GitHub : [@komi-ayola](https://github.com/komi-ayola)  
- Email : komi.developpeur@outlook.fr  

---

### ✅ Prochaines idées d’évolution
- Envoi des factures directement par e-mail.  
- Intégration d’un module de statistiques (ventes par mois, top clients).  
- Automatisation des sauvegardes (backups) en ligne.
