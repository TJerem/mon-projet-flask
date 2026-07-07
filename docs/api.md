# Documentation de l'API REST

Cette page présente les différentes routes de l'API REST proposées par l'application Flask, leurs paramètres et des exemples de réponses.

## Tableau des routes

| Route | Méthode | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Page d'accueil de l'API REST |
| `/health` | `GET` | Vérification de l'état de santé (Health Check) |
| `/hello/<name>` | `GET` | Salutation personnalisée |
| `/add/<a>/<b>` | `GET` | Addition de deux entiers |
| `/about` | `GET` | Informations sur l'application |
| `/version` | `GET` | Version de l'application |

---

## Détails et Exemples

### 1. Accueil
* **Route :** `/`
* **Méthode :** `GET`
* **Exemple de réponse :**
  ```json
  {
    "message": "Bienvenue sur mon API",
    "status": "ok"
  }
  ```

### 2. Health Check
* **Route :** `/health`
* **Méthode :** `GET`
* **Exemple de réponse :**
  ```json
  {
    "status": "healthy"
  }
  ```

### 3. Salutation personnalisée
* **Route :** `/hello/<name>`
* **Méthode :** `GET`
* **Paramètre :** `name` (chaîne de caractères dans l'URL)
* **Exemple de réponse :**
  ```json
  {
    "message": "Bonjour Docker !"
  }
  ```

### 4. Addition
* **Route :** `/add/<int:a>/<int:b>`
* **Méthode :** `GET`
* **Paramètres :** `a` (entier), `b` (entier)
* **Exemple de réponse :**
  ```json
  {
    "result": 15
  }
  ```

### 5. Informations sur l'application
* **Route :** `/about`
* **Méthode :** `GET`
* **Exemple de réponse :**
  ```json
  {
    "app": "Mon projet Flask",
    "version": "1.0"
  }
  ```

### 6. Version du projet (SemVer)
* **Route :** `/version`
* **Méthode :** `GET`
* **Exemple de réponse :**
  ```json
  {
    "version": "1.1.0"
  }
  ```
