# Compte-Rendu de TP 4 — Sécurité dans l'usine logicielle

#### Question 11 : Description de la CVE trouvée

*   **Identifiant :** [CVE-2023-30861](https://nvd.nist.gov/vuln/detail/CVE-2023-30861) / [GHSA-m2qf-hxjv-5gpq](https://github.com/advisories/GHSA-m2qf-hxjv-5gpq)
*   **Package affecté :** `Flask`
*   **Score CVSS :** 7.5 (High) — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
*   **Impact :**
    Cette vulnérabilité expose potentiellement les cookies de session permanents d'un utilisateur. Lorsque `SESSION_REFRESH_EACH_REQUEST` est activé (comportement par défaut) et que `session.permanent = True`, le cookie de session est renvoyé avec une date d'expiration mise à jour à chaque requête, même si la session n'a pas été modifiée ou accédée durant cette requête.
    Dans cette situation, Flask omet de définir l'en-tête de réponse `Vary: Cookie`. Par conséquent, si l'application est hébergée derrière un proxy de mise en cache (caching proxy) configuré pour ne pas ignorer ou supprimer les en-têtes de cookies, le proxy peut mettre en cache la réponse contenant le cookie de session d'un utilisateur et la servir à un autre utilisateur, ce qui entraîne une divulgation du cookie de session.
*   **Version corrigée :** Les versions **2.2.5** et **2.3.2** de Flask ont corrigé ce problème en garantissant que l'en-tête `Vary: Cookie` soit systématiquement ajouté.
*   **Lien vers la CVE :** [GHSA-m2qf-hxjv-5gpq (GitHub Advisory)](https://github.com/advisories/GHSA-m2qf-hxjv-5gpq)

# Compte-Rendu de TP 5 — Livraison continue (CD)

---

## Partie 1 — Dockeriser l'application Flask

### Question 1 : Explication des instructions du Dockerfile et de la copie préalable de `requirements.txt`

*   **Explication des instructions :**
    *   `FROM python:3.12-slim` : Spécifie l'image de base officielle Python 3.12 sous Debian (version allégée/slim) pour construire le conteneur.
    *   `RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*` : Met à jour la liste des paquets Debian, installe `curl` (nécessaire au health check) et nettoie les fichiers temporaires pour minimiser la taille finale de l'image.
    *   `WORKDIR /app` : Définit le répertoire de travail par défaut à `/app` pour toutes les instructions suivantes (`COPY`, `RUN`, `CMD`).
    *   `COPY requirements.txt .` : Copie le fichier `requirements.txt` de la machine hôte vers le répertoire courant (`/app`) dans le conteneur.
    *   `RUN pip install --no-cache-dir -r requirements.txt` : Installe les dépendances Python spécifiées sans conserver le cache pip afin de réduire l'espace disque.
    *   `COPY src/ ./src/` : Copie le répertoire `src/` contenant le code de l'application Flask vers `/app/src/` dans le conteneur.
    *   `HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:5000/health || exit 1` : Configure un test de santé périodique (toutes les 30s) vérifiant que l'application répond sur la route `/health`. Si 3 tentatives consécutives échouent, le conteneur est marqué comme défaillant (`unhealthy`).
    *   `EXPOSE 5000` : Indique que le conteneur écoute sur le port 5000 à titre informatif (métadonnée).
    *   `CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]` : Définit la commande par défaut à exécuter lors du lancement du conteneur, démarrant le serveur WSGI Gunicorn lié à toutes les interfaces réseau (`0.0.0.0`) sur le port 5000.
*   **Pourquoi copie-t-on `requirements.txt` avant le code source ?**
    C'est pour tirer parti du système de cache des couches (layers) de Docker. Si le code source change mais que les dépendances (`requirements.txt`) restent identiques, Docker réutilisera la couche cache générée par le `RUN pip install ...` sans réinstaller les dépendances, ce qui accélère grandement le temps de build.

### Question 2 : Différence entre une VM et un conteneur Docker et avantage principal

*   **Différence :** Une machine virtuelle (VM) virtualise le matériel physique et embarque un système d'exploitation complet invité (Guest OS) avec son propre noyau au-dessus d'un hyperviseur. Un conteneur Docker, en revanche, virtualise uniquement le système d'exploitation hôte, partageant son noyau et isolant les processus au niveau de l'espace utilisateur via les fonctionnalités Linux (namespaces et cgroups).
*   **Avantage principal :** L'extrême légèreté, la rapidité de démarrage (quelques millisecondes contre plusieurs minutes pour une VM) et la portabilité (garantie que l'application s'exécutera à l'identique sur n'importe quel environnement supportant Docker).

---

## Partie 2 — Docker Compose pour le développement local

### Question 3 : Intérêt de Docker Compose par rapport à un simple `docker run` et cas d'usage indispensable

*   **Intérêt :** Docker Compose permet de définir et de gérer des applications multi-conteneurs complexes dans un seul fichier déclaratif (`docker-compose.yml`) plutôt que de saisir de longues commandes `docker run` individuelles et manuelles. Il gère automatiquement la création des réseaux, des volumes, des variables d'environnement, et l'ordre de démarrage des services.
*   **Dans quel cas devient-il indispensable ?** Il devient indispensable lorsque l'application s'appuie sur plusieurs services interconnectés (par exemple, un serveur Flask, une base de données PostgreSQL, un cache Redis, et un reverse-proxy Nginx) qui doivent communiquer entre eux via un réseau privé commun.

---

## Partie 3 — Comprendre les registres et le tagging

### Question 4 : Pourquoi tagger une image avec plusieurs tags (SHA, version, latest) et risques de `:latest` en production

*   **Pourquoi plusieurs tags :**
    *   **Tag SHA (ex: `sha-abc1234`) :** Offre une traçabilité parfaite en liant précisément l'image au commit Git exact qui l'a produite.
    *   **Tag Version (ex: `v1.0.0`) :** Permet un versionnement sémantique clair pour les humains afin d'identifier les versions majeures/mineures stables.
    *   **Tag `latest` :** Facilite le développement en ciblant toujours la dernière version compilée sans avoir à mettre à jour manuellement les fichiers de configuration de déploiement.
*   **Pourquoi éviter `:latest` en production :** Parce que `:latest` est instable et dynamique : si une nouvelle image est poussée avec ce tag, le déploiement automatique d'un nouveau nœud tirera la nouvelle image potentiellement non testée, rompant ainsi l'immuabilité et la reproductibilité du déploiement, ce qui peut causer des pannes silencieuses ou des régressions.

### Question 5 : Qu'est-ce qu'un registre de conteneurs et comparaison de ghcr.io, Docker Hub et Google Artifact Registry

*   **Registre de conteneurs :** C'est un service de stockage et de distribution d'images de conteneurs Docker (un dépôt centralisé).
*   **Comparaison :**
    *   `ghcr.io` (GitHub Container Registry) : Parfaitement intégré à l'écosystème GitHub, gère très bien l'authentification via `GITHUB_TOKEN` de GitHub Actions, gratuit pour les dépôts publics et pratique pour regrouper code et packages.
    *   `Docker Hub` : Le registre public historique et par défaut de Docker, possédant la plus grande bibliothèque d'images officielles, mais soumis à des quotas stricts de pull pour les utilisateurs non payants.
    *   `Google Artifact Registry` (GAR) : Registre managé entreprise sur Google Cloud Platform, hautement sécurisé, performant, s'intégrant nativement avec IAM GCP et supportant d'autres types d'artefacts (npm, maven, python, etc.).

---

## Partie 4 — Automatiser le build et push dans la CI/CD

### Question 6 : Pourquoi teste-t-on le conteneur dans la CI avant de le pousser sur le registre ?

Pour s'assurer que l'image construite est pleinement opérationnelle (qu'elle démarre correctement, que les routes API répondent et que le healthcheck passe) avant de la rendre publique. Pousser une image défectueuse sur le registre polluerait l'historique et pourrait provoquer des pannes si un outil de déploiement automatique la récupérait.

### Question 7 : Explication de la condition `if: github.ref == 'refs/heads/main'` et absence de build Docker sur les Pull Requests

*   **Explication :** Cette condition restreint l'exécution du job concerné uniquement lorsque l'événement (push) se produit sur la branche par défaut `main`.
*   **Pourquoi pas sur les Pull Requests :** Parce que la condition exige explicitement d'être sur `main`. Les Pull Requests s'exécutent sur des branches de fonctionnalités (ex: `feature/docker`). Cela évite de consommer inutilement des ressources CI/CD pour builder et pousser des images Docker non validées ou en cours de développement sur le registre de production.

### Question 8 : Pourquoi utilise-t-on `${{ github.sha }}` comme tag d'image et son avantage

*   **Pourquoi le SHA :** Car le hash du commit (SHA) est unique et immuable. Chaque commit produit une image distincte et exploitable à coup sûr.
*   **Avantage :** Cela supprime l'erreur humaine (comme oublier de mettre à jour le numéro de version) et automatise totalement la livraison continue à chaque push, assurant une correspondance directe et sans équivoque entre l'état du code source et l'image Docker correspondante.

---

## Partie 5 — Gestion des versions et rollback

### Question 9 : Qu'est-ce qu'un rollback et importance du versionnement précis des images Docker

*   **Rollback :** C'est l'action de revenir rapidement à une version antérieure stable d'une application en production suite à la détection d'une anomalie ou d'un bug sur la version nouvellement déployée.
*   **Importance du versionnement précis :** Pour pouvoir pointer instantanément vers l'image de la version stable précédente (par exemple `sha-ancienne`) et la relancer à la place de l'image corrompue sans avoir à recompiler le code, garantissant un temps d'interruption (downtime) minimal.

### Question 10 : Différence entre Continuous Delivery et Continuous Deployment et implémentation dans ce TP

*   **Différence :** Dans le *Continuous Delivery* (Livraison Continue), chaque modification validée est automatiquement compilée, testée et prête à être déployée, mais la mise en production nécessite une validation ou action humaine manuelle (déplenchement en 1 clic). Dans le *Continuous Deployment* (Déploiement Continu), le processus est entièrement automatisé du commit jusqu'à la mise en production sans aucune intervention humaine intermédiaire.
*   **Dans ce TP :** Nous avons mis en place de la **Livraison Continue (Continuous Delivery)** car les images sont construites, testées et publiées automatiquement sur le registre de conteneurs (`ghcr.io`), mais aucun déploiement automatique sur un serveur de production (hébergeur cloud, cluster Kubernetes, etc.) n'est configuré pour consommer l'image immédiatement.

### Question 11 : Risques du déploiement automatique et atténuation

*   **Risques :**
    *   Déploiement d'une régression critique ou d'une faille de sécurité passée au travers des mailles de la CI.
    *   Interruption de service (downtime) lors du déploiement si la transition n'est pas progressive.
    *   Incompatibilité soudaine avec la base de données (migrations de schéma).
*   **Atténuation :**
    *   Mettre en place une couverture de tests automatisés robuste (tests d'intégration, de sécurité et bout-en-bout) dans la CI.
    *   Utiliser des stratégies de déploiement progressif comme le *Blue-Green deployment* ou le *Canary deployment*.
    *   Implémenter des mécanismes de rollback automatique basés sur le monitoring de santé (health check) en production.
    *   Assurer la rétrocompatibilité des migrations de base de données.

---

## Partie 6 — Recherche autonome

### Question 12 : Expliquez le principe du multi-stage build, ses avantages, le Dockerfile modifié et la différence de taille

*   **Principe :** Il consiste à utiliser plusieurs instructions `FROM` temporaires au sein d'un unique `Dockerfile`. Chaque section (stage) peut utiliser une image de base différente. On peut copier sélectivement les artefacts générés (fichiers compilés, dépendances installées) d'une étape vers l'autre.
*   **Avantages :**
    *   **Taille :** En excluant les compilateurs, les outils de développement/CI (comme `pytest`, `black`, `ruff`, `bandit`, `semgrep`, `pip-audit`) et les caches de package de l'image finale, l'image de production est drastiquement réduite.
    *   **Sécurité :** Réduit la surface d'attaque en éliminant les binaires et packages inutiles qui pourraient comporter des vulnérabilités exploitables par un attaquant en cas d'intrusion.
*   **Dockerfile modifié :**
    ```dockerfile
    # Etape 1: Builder
    FROM python:3.12-slim AS builder
    WORKDIR /app
    RUN pip install --no-cache-dir --user flask gunicorn

    # Etape 2: Runner
    FROM python:3.12-slim AS runner
    WORKDIR /app
    RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
    COPY --from=builder /root/.local /root/.local
    COPY src/ ./src/
    ENV PATH=/root/.local/bin:$PATH
    HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
      CMD curl -f http://localhost:5000/health || exit 1
    EXPOSE 5000
    CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
    ```
*   **Différence de taille :**
    *   Taille image simple-stage : **752 Mo**
    *   Taille image multi-stage (optimisée) : **211 Mo**
    *   Gain d'espace : **541 Mo (réduction de ~72%)**
*   **Lien vers la documentation consultée :** [Docker Multi-stage builds documentation](https://docs.docker.com/build/building/multi-stage/)
