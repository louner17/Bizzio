import os
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from .auth_config import get_oauth_client

router = APIRouter(tags=["Auth"])

ALLOWED_EMAILS = {
    "bbartekpawlowski@gmail.com",
    "AlexjaandAlexja27@gmail.com"
}
async def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login')
    if user.get("email") not in ALLOWED_EMAILS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu.")
    return user

@router.get('/login')
async def login(request: Request):
    oauth = get_oauth_client()
    if not oauth:
        raise HTTPException(status_code=500, detail="Konfiguracja OAuth niedostępna.")
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@router.get('/auth', name='auth')
async def auth(request: Request):
    oauth = get_oauth_client()
    if not oauth:
        raise HTTPException(status_code=500, detail="Konfiguracja OAuth niedostępna.")
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/dashboard')

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/login')