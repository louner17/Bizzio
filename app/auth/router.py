from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os

# ZMIANA: Przenosimy odczyt zmiennych do funkcji, aby nie blokowały startu
def get_oauth_client():
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not google_client_id or not google_client_secret:
        # W środowisku produkcyjnym to powinno być traktowane jako błąd krytyczny
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

# Zmień te adresy na swoje!
ALLOWED_EMAILS = {
    "bbartekpawlowski@gmail.com",
    "AlexjaandAlexja27@gmail.com"
}

router = APIRouter(tags=["Auth"])

async def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login')
    if user.get("email") not in ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="Brak dostępu dla tego konta Google.")
    return user

@router.get('/login')
async def login(request: Request):
    oauth_client = get_oauth_client()
    if not oauth_client:
        raise HTTPException(status_code=500, detail="Konfiguracja OAuth nie jest dostępna.")
    redirect_uri = request.url_for('auth')
    return await oauth_client.google.authorize_redirect(request, str(redirect_uri))

@router.get('/auth', name='auth')
async def auth(request: Request):
    oauth_client = get_oauth_client()
    if not oauth_client:
        raise HTTPException(status_code=500, detail="Konfiguracja OAuth nie jest dostępna.")
    token = await oauth_client.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/dashboard')

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/login')