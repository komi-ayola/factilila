# Factilila - Système de Facturation
Factilila est une application web de gestion de factures développée avec Django. Elle permet aux utilisateurs de créer, gérer et générer des factures ou proformas au format PDF, avec prise en charge des clients, des lignes de facture, des taxes (TVA), et des frais de livraison.
Fonctionnalités

## Création et modification de factures ou proformas.
Gestion des clients.
Ajout de lignes de facture (produits, quantités, prix unitaires).
Calcul automatique des totaux (HT, TVA, TTC).
Gestion des frais de livraison.
Génération de factures au format PDF avec un design personnalisé.
Conversion des montants en lettres (par exemple, "sept cent huit mille Francs CFA").

## Prérequis
Avant d’installer Factilila, assurez-vous d’avoir les éléments suivants :

Python : Version 3.12.4 ou supérieure.
pip : Gestionnaire de packages Python.
Virtualenv (recommandé) : Pour créer un environnement virtuel.
Git : Pour cloner le dépôt.
WeasyPrint : Pour générer les PDF (nécessite des dépendances système comme GTK+ sur Windows).

## Installation

Cloner le dépôt :
git clone https://github.com/komi-ayola/factilila.git
cd factilila


## Créer un environnement virtuel (facultatif mais recommandé) :
python -m venv env
source env/bin/activate  # Sur Windows : env\Scripts\activate


## Installer les dépendances :Assurez-vous d’avoir un fichier requirements.txt avec les dépendances suivantes (crée-le si nécessaire) :
Django==5.1
django-weasyprint==2.2.1
weasyprint==62.3

## Ensuite, installez-les :
pip install -r requirements.txt


## Installer WeasyPrint (dépendances système) :

Sur Windows, téléchargez et installez GTK+ (nécessaire pour WeasyPrint) : Télécharger GTK+.
Suivez les instructions d’installation de WeasyPrint : Documentation WeasyPrint.


## Appliquer les migrations :
python manage.py makemigrations
python manage.py migrate


Créer un superutilisateur (optionnel) :Si tu veux accéder à l’interface d’administration Django :
python manage.py createsuperuser



Lancer l’application

## Démarrer le serveur :
python manage.py runserver


## Accéder à l’application :

Ouvre ton navigateur et va à http://127.0.0.1:8000/.
Si tu as créé un superutilisateur, accède à l’administration sur http://127.0.0.1:8000/admin/.



# Utilisation

## Créer une facture :

Va sur http://127.0.0.1:8000/factures/ajouter/.
Remplis les champs (client, date, objet, TVA, frais de livraison, etc.).
Ajoute des lignes de facture (produits, quantités, prix).
Sauvegarde pour créer la facture.


## Voir les détails et générer un PDF :

Va sur http://127.0.0.1:8000/factures/detail/<id>/ (par exemple, /factures/detail/1/).
Clique sur "Télécharger PDF" pour générer une facture au format PDF.



# Contribution
## Les contributions sont les bienvenues ! Si tu souhaites contribuer :

Fork le projet.
Crée une branche pour ta fonctionnalité (git checkout -b feature/ma-fonctionnalite).
Commit tes changements (git commit -m "Ajout de ma fonctionnalité").
Push vers ta branche (git push origin feature/ma-fonctionnalite).
Ouvre une Pull Request.

Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
Contact
Pour toute question ou suggestion, contacte-moi via GitHub ou à komi.developpeur@outlook.fr.
