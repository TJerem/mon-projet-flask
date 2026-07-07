# Compte-Rendu de TP 4 — Sécurité dans l'usine logicielle

Ce document présente les réponses et réalisations pour la **Partie 6 — Recherche autonome** du TP 4.

---

## Partie 6 — Recherche autonome

### 6.1 — Rechercher une CVE Flask

#### Question 11 : Description de la CVE trouvée

*   **Identifiant :** [CVE-2023-30861](https://nvd.nist.gov/vuln/detail/CVE-2023-30861) / [GHSA-m2qf-hxjv-5gpq](https://github.com/advisories/GHSA-m2qf-hxjv-5gpq)
*   **Package affecté :** `Flask`
*   **Score CVSS :** 7.5 (High) — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
*   **Impact :**
    Cette vulnérabilité expose potentiellement les cookies de session permanents d'un utilisateur. Lorsque `SESSION_REFRESH_EACH_REQUEST` est activé (comportement par défaut) et que `session.permanent = True`, le cookie de session est renvoyé avec une date d'expiration mise à jour à chaque requête, même si la session n'a pas été modifiée ou accédée durant cette requête.
    Dans cette situation, Flask omet de définir l'en-tête de réponse `Vary: Cookie`. Par conséquent, si l'application est hébergée derrière un proxy de mise en cache (caching proxy) configuré pour ne pas ignorer ou supprimer les en-têtes de cookies, le proxy peut mettre en cache la réponse contenant le cookie de session d'un utilisateur et la servir à un autre utilisateur, ce qui entraîne une divulgation du cookie de session.
*   **Version corrigée :** Les versions **2.2.5** et **2.3.2** de Flask ont corrigé ce problème en garantissant que l'en-tête `Vary: Cookie` soit systématiquement ajouté.
*   **Lien vers la CVE :** [GHSA-m2qf-hxjv-5gpq (GitHub Advisory)](https://github.com/advisories/GHSA-m2qf-hxjv-5gpq)

#### Rôle de pip-audit et Dependabot pour prévenir ce problème

1.  **pip-audit :**
    En exécutant `pip-audit` localement ou dans le pipeline CI, l'outil analyse les dépendances installées ou déclarées dans `requirements.txt` et interroge les bases de vulnérabilités connues (comme PyPI). Si une version vulnérable de Flask (inférieure à 2.2.5 ou 2.3.2) est détectée, `pip-audit` renvoie un code d'erreur non nul, bloquant ainsi le pipeline et affichant les détails de la faille de sécurité ainsi que les versions corrigées recommandées.

2.  **Dependabot :**
    Grâce au fichier de configuration `.github/dependabot.yml`, Dependabot vérifie de façon hebdomadaire (ou quotidienne selon la configuration) la présence de dépendances obsolètes ou vulnérables dans le projet. Dès qu'une vulnérabilité est publiée dans la base GitHub Advisory (comme la faille ci-dessus), Dependabot ouvre automatiquement une Pull Request sur le dépôt pour mettre à jour la dépendance vers la version corrigée minimale (par exemple, de `flask==2.2.0` à `flask==2.2.5`).

---

### 6.2 — Sécuriser une route Flask

#### Implémentation des bonnes pratiques de sécurité

Pour renforcer la sécurité de l'application Flask sans ajouter de dépendances tierces superflues, nous avons implémenté des en-têtes HTTP de sécurité globaux via le hook `@app.after_request` dans le fichier [app.py](file:///home/jerem/mon-projet-flask/src/app.py) :

1.  **`X-Frame-Options: DENY` :** Empêche l'application d'être intégrée dans des `<frame>`, `<iframe>` ou `<object>`, protégeant ainsi l'utilisateur contre les attaques de type Clickjacking (détournement de clic).
2.  **`Content-Security-Policy: default-src 'self'` :** Restreint le chargement des ressources (scripts, images, styles, etc.) uniquement depuis l'origine de l'application elle-même, réduisant considérablement le risque d'attaques par injection de contenu (XSS).
3.  **`X-Content-Type-Options: nosniff` :** Empêche le navigateur de deviner (MIME-sniffing) le type de contenu de la réponse et le force à respecter strictement le Content-Type déclaré (par exemple `application/json`), évitant ainsi l'exécution involontaire de code malveillant déguisé.

Les modifications ont été validées à l'aide de nouveaux tests unitaires ajoutés dans [test_app.py](file:///home/jerem/mon-projet-flask/tests/test_app.py) qui vérifient la présence et la valeur de ces en-têtes sur plusieurs routes de l'API.
