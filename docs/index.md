# Accueil - Mon Projet Flask

Bienvenue sur la documentation officielle de **Mon Projet Flask** !

Ce projet est une API REST développée avec le framework **Flask** en Python. Il a été conçu pour illustrer la mise en place d'une usine logicielle complète et robuste en appliquant les meilleures pratiques DevOps :

* **Intégration Continue (CI) :** Validation du code (linters Black & Ruff), audit de sécurité (Bandit & Semgrep) et tests unitaires automatisés (Pytest avec rapports de couverture).
* **Livraison Continue (CD) :** Containerisation via Docker (multi-stage builds) et orchestration locale (Docker Compose).
* **Déploiement Continu :** Hébergement automatisé et sécurisé sur Google Cloud Run avec automatisation des releases (SemVer via `release-please`).
* **Documentation as Code :** Site de documentation dynamique généré avec **MkDocs** et déployé automatiquement sur **GitHub Pages**.

## Structure de la documentation
Pour naviguer à travers la documentation, veuillez utiliser le menu :
* **[API](api.md) :** Détail des routes de l'API REST et leurs spécifications.
* **[Architecture](architecture.md) :** Architecture de l'application et schéma de notre pipeline CI/CD.
* **[Contribution](contributing.md) :** Guide pour participer au projet et installer l'environnement de développement.
