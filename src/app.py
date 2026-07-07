import os

from flask import Flask, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-insecure")


@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/")
def home():
    """Route d'accueil de l'API Flask.

    Retourne un message de bienvenue au format JSON.
    """
    return jsonify({"message": "Bienvenue sur mon API", "status": "ok"})


@app.route("/health")
def health():
    """Route de test d'état de santé (healthcheck) de l'API.

    Retourne l'état de l'application (healthy) au format JSON.
    """
    return jsonify({"status": "healthy"})


@app.route("/hello/<name>")
def hello(name):
    """Route de salutation personnalisée.

    Prend en paramètre le nom de l'utilisateur et retourne une salutation personnalisée.
    """
    return jsonify({"message": f"Bonjour {name} !"})


if __name__ == "__main__":
    app.run()


@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    """Route de calcul d'addition.

    Prend deux entiers en paramètres d'URL et retourne leur somme au format JSON.
    """
    return jsonify({"result": a + b})


@app.route("/about")
def about():
    return jsonify({"app": "Mon projet Flask", "version": "1.0"})


@app.route("/version")
def version():
    return jsonify({"version": "1.1.0"})
