import os
from authlib.integrations.starlette_client import OAuth

oauth = None

def get_oauth_client():
    """Zwraca skonfigurowaną instancję OAuth lub None, jeśli brakuje zmiennych."""
    global oauth
    if oauth is not None:
        return oauth

    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not google_client_id or not google_client_secret:
        print("BŁĄD KRYTYCZNY: Brak GOOGLE_CLIENT_ID lub GOOGLE_CLIENT_SECRET")
        return None

    oauth = OAuth()
    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    return oauth