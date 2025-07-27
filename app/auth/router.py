from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
import os

# Pobieramy dane ze zmiennych środowiskowych, które ustawimy w GCP
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY", "domyslny_sekret_do_testow_lokalnych")

# Zmień te adresy na swoje!
ALLOWED_EMAILS = {
    "bbartekpawlowski@gmail.com",
    "AlexjaandAlexja27@gmail.com"
}

router = APIRouter(tags=["Auth"])
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- Zależność do sprawdzania, czy użytkownik jest zalogowany ---
async def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login')
    if user.get("email") not in ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="Brak dostępu dla tego konta Google.")
    return user

# --- Endpointy API ---
@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@router.get('/auth', name='auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/dashboard')

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/login')