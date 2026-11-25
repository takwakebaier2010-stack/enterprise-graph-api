"""Serveur du dashboard (aucune modification du projet, aucune installation).

Usage :
    1) Lancer le projet Django comme d'habitude :  python manage.py runserver
    2) Dans un autre terminal, depuis CE dossier :  python serve_dashboard.py
    3) Ouvrir http://127.0.0.1:5000

Ce petit serveur affiche dashboard.html et relaie les requêtes GraphQL vers Django,
ce qui évite tout problème de CORS sans toucher au dépôt.

Il envoie aussi lui-même un jeton CSRF (cookie + en-tête) pour que Django
accepte les POST sans avoir à modifier le projet.

Options (variables d'environnement) :
    BACKEND  adresse de Django   (défaut http://127.0.0.1:8000)
    PORT     port du dashboard   (défaut 5000)
"""
import json
import os
import secrets
import string
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BACKEND = os.environ.get("BACKEND", "http://127.0.0.1:8000").rstrip("/")
PORT = int(os.environ.get("PORT", "5000"))
HERE = os.path.dirname(os.path.abspath(__file__))
ROUTES = {"/api/classic": "/graphql/", "/api/optimized": "/graphql-optimized/"}

# Jeton CSRF généré une fois au démarrage (Django compare cookie et en-tête)
_ALPHABET = string.ascii_letters + string.digits
CSRF_TOKEN = "".join(secrets.choice(_ALPHABET) for _ in range(64))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html", "/dashboard.html"):
            with open(os.path.join(HERE, "dashboard.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        target = ROUTES.get(self.path.split("?")[0])
        if not target:
            return self._send(404, b'{"error":"not found"}')
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        req = urllib.request.Request(
            BACKEND + target, data=data, method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Cookie": f"csrftoken={CSRF_TOKEN}",
                "X-CSRFToken": CSRF_TOKEN,
                "Referer": BACKEND + "/",
                "Origin": BACKEND,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                self._send(r.status, r.read())
        except urllib.error.HTTPError as e:  # erreurs GraphQL renvoyées en 4xx/5xx
            self._send(e.code, e.read() or b"{}")
        except Exception as e:
            msg = f"Django injoignable sur {BACKEND} ({e}). Avez-vous lancé 'python manage.py runserver' ?"
            self._send(502, json.dumps({"errors": [{"message": msg}]}).encode())

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"Dashboard : http://127.0.0.1:{PORT}   (API Django : {BACKEND})")
    print("Ctrl+C pour arrêter.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
