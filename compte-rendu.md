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

# Compte-Rendu de TP 6 — Gestion des artefacts

---

## Partie 0 — État des lieux

### Question 1 : Qu'est-ce qu'un artefact dans le contexte d'une usine logicielle ? Donnez 3 exemples d'artefacts différents.

Dans le contexte d'une usine logicielle, un **artefact** est un fichier généré, compilé ou produit automatiquement par le pipeline CI/CD (les étapes de build, de test ou d'empaquetage). Cet objet est généralement stocké de manière durable et immuable dans un registre ou un gestionnaire d'artefacts pour être déployé, distribué ou réutilisé plus tard.

*Exemples d'artefacts différents :*
1. **Une image de conteneur (ex: Image Docker)** publiée sur un registre d'images (comme GHCR, Artifact Registry ou Docker Hub) prête à être déployée.
2. **Un paquet de bibliothèque redistribuable (ex: fichier `.whl` Python sur PyPI, ou package npm sur npmjs)** prêt à être installé comme dépendance.
3. **Un rapport de qualité ou de couverture de code (ex: fichier HTML/JSON généré par pytest-cov ou SonarQube)** archivé pour archivage ou audit.

---

## Partie 1 — Multi-tagging des images Docker

### Question 2 : Pourquoi tagger une image avec plusieurs tags (SHA complet, SHA court, latest) ? Dans quel cas utilise-t-on chacun ?

Le multi-tagging offre à la fois traçabilité, flexibilité de développement et sécurité de production :
* **SHA complet (hash Git de 40 caractères) :** Fournit un identifiant unique, immuable et non ambigu pour chaque commit. On l'utilise principalement pour le déploiement en production afin de garantir que la version exacte du code validée en CI/CD est celle qui tourne sur les serveurs, évitant toute confusion.
* **SHA court (7 caractères) :** Plus lisible et compact que le SHA complet. On l'utilise lors des opérations manuelles de débogage ou d'administration (par exemple pour lister, inspecter ou tirer une image rapidement en ligne de commande : `docker pull image:sha-abc1234`).
* **latest :** Pointeur mobile pointant vers l'image la plus récente construite sur la branche principale (`main`). On l'utilise uniquement en environnement de développement local ou de staging pour simplifier les tests (pas besoin de changer de tag à chaque commit), mais il est fortement proscrit en production en raison de son manque d'immuabilité.

---

## Partie 2 — Versioning sémantique (SemVer)

### Question 3 : Expliquez le versioning sémantique (SemVer). Pour chaque cas, indiquez si c'est un changement MAJOR, MINOR ou PATCH : ajout d'une route, correction d'un bug, changement du format de réponse JSON.

Le versioning sémantique (SemVer) est un standard de numérotation de version sous le format `MAJOR.MINOR.PATCH` (ex: `1.4.2`), où chaque nombre s'incrémente selon l'impact de la modification sur l'API publique :
* **PATCH** est incrémenté pour les corrections de bugs rétrocompatibles.
* **MINOR** est incrémenté pour l'ajout de nouvelles fonctionnalités rétrocompatibles.
* **MAJOR** est incrémenté pour des modifications majeures introduisant des ruptures de compatibilité ascendante (breaking changes).

*Classification des cas demandés :*
* **Ajout d'une route :** Changement **MINOR** (nouvelle fonctionnalité qui ne casse pas l'existant).
* **Correction d'un bug :** Changement **PATCH** (correctif rétrocompatible).
* **Changement du format de réponse JSON :** Changement **MAJOR** (rompt la compatibilité avec les clients existants qui consomment l'API, nécessitant une mise à jour de leur côté).

### Question 4 : Quelle est la différence entre un tag Git léger (git tag v1.0) et un tag annoté (git tag -a v1.0 -m "...") ?

* **Tag Git léger (Lightweight tag) :** C'est un simple pointeur (une référence) vers un commit spécifique, similaire à une branche qui ne bougerait pas. Il ne contient aucune métadonnée supplémentaire.
* **Tag Git annoté (Annotated tag) :** C'est un objet Git complet stocké en base de données. Il contient le nom de l'auteur du tag, son adresse e-mail, la date de création du tag, une signature GPG optionnelle et un message d'annotation (fourni avec `-m`). C'est le type de tag recommandé pour marquer officiellement les releases de production en raison de sa traçabilité et de sa pérennité.

---

## Partie 3 — Releases GitHub automatisées

### Question 5 : Comment release-please détermine-t-il le numéro de version à partir des commits ? Quel est le lien avec les Conventional Commits ?

`release-please` utilise l'historique des messages de commit basés sur le standard **Conventional Commits** (ex: `feat: ...`, `fix: ...`, `feat!: ...` ou `BREAKING CHANGE: ...`) pour analyser le type de changement effectué depuis la dernière release :
* Si des commits de type `fix:` sont trouvés, `release-please` incrémente le numéro de **PATCH** (ex: `1.0.0` -> `1.0.1`).
* Si des commits de type `feat:` sont trouvés, il incrémente le numéro de **MINOR** (ex: `1.0.0` -> `1.1.0`).
* Si un point d'exclamation ou la mention `BREAKING CHANGE:` est présente dans un commit (ex: `feat!: ...`), il incrémente le numéro de **MAJOR** (ex: `1.0.0` -> `2.0.0`).

### Question 6 : Quel est l'avantage d'automatiser les releases plutôt que de les créer manuellement ?

L'automatisation offre plusieurs avantages majeurs :
* **Fiabilité et consistance :** Élimine le risque d'erreur humaine (comme un mauvais tag, un oubli de mise à jour de version dans `pyproject.toml`, ou des releases désynchronisées).
* **Génération automatique du Changelog :** Rassemble de façon claire et immédiate la liste de toutes les nouveautés, correctifs et breaking changes apportés par la version, sans rédaction manuelle.
* **Gain de temps :** Le développeur a simplement besoin d'écrire des commits structurés, et le reste du flux de livraison (tagging, changelog, publication, déploiement) est géré automatiquement par la CI/CD.

---

## Partie 4 — Pipeline de release complet

### Question 7 : Décrivez le pipeline de release complet, du commit au déploiement. Combien de workflows sont impliqués et quel est leur rôle ?

Le pipeline complet de release implique **2 workflows** distincts :

1. **Workflow de Qualité / Intégration Continue (`ci.yml`) :**
   * **Déclenchement :** À chaque push sur n'importe quelle branche ou Pull Request.
   * **Rôle :** Exécuter les vérifications de qualité de code (Black, Ruff), de sécurité (Bandit, Semgrep, pip-audit) et lancer les tests unitaires/de couverture. Il garantit que le code proposé est stable et sécurisé.
2. **Workflow de Release / Déploiement Continu (`release.yml`) :**
   * **Déclenchement :** À chaque push sur la branche principale `main`.
   * **Rôle :**
     * Exécuter `release-please-action` pour détecter les Conventional Commits.
     * Créer/mettre à jour la Pull Request de release proposant le bump de version et le changelog.
     * Une fois cette PR de release mergée par un humain, le workflow crée automatiquement le tag de version Git (ex: `v1.1.0`) et la release GitHub.
     * Suite à la création de cette release, il exécute le job `deploy-release` pour s'authentifier sur GCP, construire l'image Docker multi-stage taggée avec le tag SemVer exact, la pousser sur Artifact Registry et la déployer sur Cloud Run.

---

### Question 8 : Quelle est la différence entre déployer avec github.sha (TP5) et déployer avec un tag de version SemVer (ce TP) ? Quand utiliser chacun ?

* **Déployer avec `github.sha` :**
   * *Principe :* Chaque commit sur `main` compile et déploie immédiatement une image unique taggée par son hash SHA.
   * *Quand l'utiliser :* Idéal pour le développement continu et le staging rapide afin de tester en continu le code dès qu'il est poussé.
* **Déployer avec un tag de version SemVer :**
   * *Principe :* L'image de production n'est générée et déployée que lorsqu'une version officielle et validée (ex: `v1.1.0`) est créée par fusion de la PR de release.
   * *Quand l'utiliser :* C'est la bonne pratique absolue en production (environnement de Release) car elle garantit que seuls les incréments stables et explicitement validés par l'équipe sont mis en production, facilitant l'identification des versions en cours et la gestion des rollbacks.

---

### Question 9 : Pourquoi le principe d'immutabilité des artefacts est-il important ? Que se passe-t-il si on écrase un tag Docker existant ?

* **Importance de l'immutabilité :** L'immutabilité garantit qu'un artefact (par exemple l'image `v1.0.0`) ne changera plus jamais une fois publié. Cela assure la reproductibilité et la prédictibilité absolue des déploiements.
* **Si on écrase un tag existant (ex: repousser une nouvelle version sous le tag `v1.0.0` existant) :**
   * Le déploiement d'un nouveau conteneur tirera une image différente de celle qui a été testée et validée à l'origine sous ce tag.
   * Il devient impossible de savoir exactement quel code tourne en production.
   * Le rollback vers une version stable connue devient impossible ou corrompu, ce qui compromet gravement la fiabilité et la sécurité de l'infrastructure.

---

## Partie 5 — Recherche autonome

### Question 10 : Analyse des releases d'un projet open source (FastAPI)

Pour cette analyse, nous avons choisi le projet populaire **FastAPI**.
* **Lien vers la page Releases :** [https://github.com/fastapi/fastapi/releases](https://github.com/fastapi/fastapi/releases)
* **Analyse des 5 dernières versions (au mois de juin 2026) :**
  * `0.138.1` (PATCH) : Résout des bugs mineurs et des avertissements.
  * `0.138.0` (MINOR) : Ajoute de nouvelles fonctionnalités et met à jour des composants internes de routage rétrocompatibles.
  * `0.137.2` (PATCH) : Résout un correctif de sécurité et met à jour des dépendances.
  * `0.137.1` (PATCH) : Corrige des bugs d'intégration de typage.
  * `0.137.0` (MINOR) : Ajout de fonctionnalités de validation de schémas.
* **Tags et SemVer :** Oui, les versions de FastAPI suivent strictement le standard SemVer (bien que le numéro de version majeure reste à `0` pour indiquer que le framework continue d'évoluer, les composants mineurs et patchs suivent les règles standards).
* **Automatisation et Outils :** FastAPI utilise des scripts d'automatisation personnalisés combinés avec des GitHub Actions pour générer le changelog à partir des labels des PRs fusionnées, et automatiser les releases sur GitHub et la publication des paquets sur PyPI.
