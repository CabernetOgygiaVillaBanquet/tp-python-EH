import hashlib
import hmac
import json
import time

# Clé secrète partagée entre le client et le serveur
SECRET_KEY = b"supersecretkey123"

def timestamp():
    """Retourne le timestamp actuel en secondes."""
    return int(time.time())

def make_hmac(data: bytes) -> str:
    """Crée un HMAC SHA256 pour authentifier les données."""
    h = hmac.new(SECRET_KEY, data, hashlib.sha256)
    return h.hexdigest()

def verify_hmac(data: bytes, signature: str) -> bool:
    """Vérifie qu'un HMAC est valide."""
    expected = make_hmac(data)
    return hmac.compare_digest(expected, signature)

def json_safe_loads(s: str):
    """Charge du JSON de manière sécurisée, retourne None en cas d'erreur."""
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
