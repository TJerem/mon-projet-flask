# Guide de Contribution

Merci de prendre le temps de contribuer à ce projet ! Voici les directives à suivre pour soumettre vos modifications et suggestions.

## Comment contribuer

### 1. Signaler un bug
Si vous rencontrez un problème avec l'application, merci d'ouvrir une issue de type **Bug Report** en décrivant :
* Les étapes détaillées pour reproduire le bug.
* Le comportement attendu et le comportement obtenu.
* Votre environnement technique (OS, version de Python, Docker).

### 2. Proposer une fonctionnalité
Pour suggérer des améliorations ou de nouvelles fonctionnalités, merci d'ouvrir une issue de type **Feature Request** afin de discuter de l'idée en amont.

### 3. Soumettre une Pull Request (PR)
1. Créez une branche de fonctionnalité dédiée à partir de `main` (ex: `feature/ma-fonctionnalite`).
2. Réalisez vos modifications dans cette branche.
3. Assurez-vous que toutes les vérifications de qualité de code et tous les tests passent localement.
4. Ouvrez une Pull Request décrivant vos changements.

---

## Conventions du projet

### Messages de Commit (Conventional Commits)
Le projet suit strictement la spécification des **Conventional Commits**. Vos messages de commit doivent être formatés ainsi :
* `feat: ...` : Ajout d'une nouvelle fonctionnalité (MINOR).
* `fix: ...` : Correction d'un bug (PATCH).
* `docs: ...` : Modifications de la documentation.
* `chore: ...` : Tâches courantes (maintenance, configuration).
* Les changements incompatibles (breaking changes) doivent être marqués par un `!` après le type (ex: `feat!: ...`) ou inclure `BREAKING CHANGE: ...` en pied de commit.

### Qualité du Code
* **Formatage :** Le code Python doit être formaté à l'aide de **Black** avec une longueur de ligne maximale de **120 caractères**.
* **Linter :** Le code doit être conforme aux règles configurées dans **Ruff**.
* **Tests unitaires :** Les nouveaux développements doivent être accompagnés de tests unitaires avec **pytest**. La couverture globale de tests doit rester supérieure ou égale à **70%**.

Vous pouvez lancer les validations locales via la commande :
```bash
black src/ tests/
ruff check src/ tests/
pytest --cov=src --cov-fail-under=70
```
