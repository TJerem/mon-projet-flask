# Mon Projet Flask

![CI](https://github.com/TJerem/mon-projet-flask/actions/workflows/ci.yml/badge.svg)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/TJerem/mon-projet-flask)](https://github.com/TJerem/mon-projet-flask/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-green.svg)](https://TJerem.github.io/mon-projet-flask/)

> API REST Flask avec un pipeline CI/CD moderne, des analyses de sécurité et de qualité poussées, et déployée automatiquement sur Google Cloud Run.

La documentation complète du projet est disponible en ligne sur **[GitHub Pages](https://TJerem.github.io/mon-projet-flask/)**.

---

## Installation et Utilisation Locale

### Prérequis
* Python 3.12+
* Docker & Docker Compose (facultatif, pour la conteneurisation)

### Lancement avec Python
```bash
# 1. Cloner le dépôt
git clone https://github.com/TJerem/mon-projet-flask.git
cd mon-projet-flask

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Linux/macOS
# ou
.venv\Scripts\activate     # Sur Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python src/app.py
```

### Lancement avec Docker Compose
```bash
docker compose up --build
```
L'application sera accessible sur [http://localhost:5000](http://localhost:5000).

---

## Routes API de l'Application

| Route | Méthode | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Message d'accueil de l'API |
| `/health` | `GET` | Test de l'état de santé (Health Check) |
| `/hello/<name>` | `GET` | Salutation personnalisée |
| `/add/<a>/<b>` | `GET` | Addition de deux entiers |
| `/about` | `GET` | Informations sur l'application |
| `/version` | `GET` | Version sémantique de l'application |

---

## Usine Logicielle (CI/CD)

### Intégration Continue (CI)
Le workflow `ci.yml` s'exécute à chaque push ou PR et valide :
* **Qualité :** Tri des imports, formatage Black et linter Ruff.
* **Sécurité :** Analyse statique par Bandit et Semgrep, détection de secrets par Gitleaks et audit des CVE par pip-audit.
* **Tests :** Exécution avec pytest (couverture de code minimale de 70%).

### Déploiement Continu (CD)
Le workflow `release.yml` est déclenché par `release-please` lors de la fusion d'une Pull Request de release :
* Génère automatiquement le changelog et le tag de version SemVer (ex: `v1.1.0`).
* Construit une image Docker de production via un processus multi-stage.
* Déploie automatiquement sur **Google Cloud Run**.
