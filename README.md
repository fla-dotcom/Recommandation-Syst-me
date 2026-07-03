# Hybrid Educational Recommendation System

## Description

Ce projet présente un système de recommandation pédagogique hybride pour une plateforme d'e-learning développé dans le cadre d'un mémoire de Master.


Le système combine :

- Filtrage collaboratif (SVD)
- Filtrage basé sur le contenu (TF-IDF)
- Facteur de popularité
- Application Web développée avec Django
- Système de tracking automatique des interactions utilisateurs

Le modèle final retenu est :

Score=0.60×SVD+0.25×TF−IDF+0.15×Popularité

Contenu du dépôt

Le dépôt contient notamment :

- Prétraitement du dataset MARS
- Construction des modèles de recommandation
- Évaluation expérimentale (RMSE, Hit Rate@K)
- Intégration du moteur de recommandation
- Application Web Django
- Tracking automatique des interactions utilisateurs

## Dataset

Mandarine Academy Recommender System (MARS)

## Technologies

- Python
- Surprise
- Pandas
- NumPy
- Scikit-learn
- Django
- Bootstrap
- Python 3.12
- PostgreSQL


```bash
python manage.py runserver
```

Année universitaire : 2025–2026


