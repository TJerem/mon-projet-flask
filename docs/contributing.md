# Guide de Contribution

Bienvenue ! Ce guide décrit comment configurer votre environnement de développement local, soumettre des modifications et respecter les conventions de notre usine logicielle.

## Configuration locale

### Prérequis
* Python 3.12+
* Docker & Docker Compose
* Git

### Installation du projet
1. Cloner le dépôt Git :
   ```bash
   git clone https://github.com/TJerem/mon-projet-flask.git
   cd mon-projet-flask
   ```
2. Créer et activer l'environnement virtuel :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Sur Linux/macOS
   # ou
   .venv\Scripts\activate     # Sur Windows
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Lancer l'application en mode local :
   ```bash
   python src/app.py
   ```

---

## Lancement des outils de validation

Avant de proposer des modifications, veuillez exécuter ces commandes localement pour vous assurer de la conformité du code :

### 1. Formater le code (Black)
```bash
black src/ tests/
```

### 2. Valider le style et les règles de codage (Ruff)
```bash
ruff check src/ tests/
```

### 3. Lancer les tests unitaires et mesurer la couverture (Pytest)
```bash
pytest --cov=src --cov-report=term-missing
```
*Le pipeline CI échouera si la couverture descend sous les **70%**.*

### 4. Lancer le site de documentation localement
```bash
mkdocs serve
```
Le site sera alors accessible à l'adresse [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Conventions de Commit

Nous appliquons la spécification **Conventional Commits**. Chaque commit doit utiliser un préfixe significatif :
* `feat:` pour ajouter une nouvelle fonctionnalité (MINOR).
* `fix:` pour corriger un bug (PATCH).
* `docs:` pour modifier la documentation.
* `chore:` pour des tâches de maintenance, la CI/CD ou la gestion de version.
