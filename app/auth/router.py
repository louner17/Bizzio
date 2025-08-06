import os
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

router = APIRouter(tags=["Auth"])
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
ALLOWED_EMAILS = {
    "bbartekpawlowski@gmail.com",
    "AlexjaandAlexja27@gmail.com"
}
# Zależność sprawdzająca, czy użytkownik jest zalogowany i autoryzowany
async def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        # Jeśli nie ma sesji, przekieruj do strony logowania Google
        return RedirectResponse(url='/login')
    if user.get("email") not in ALLOWED_EMAILS:
        # Jeśli email nie jest na liście, zablokuj dostęp
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu dla tego konta.")
    return user

# Endpointy
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
    return RedirectResponse(url='/')