# from fastapi import FastAPI, Request, status, Depends
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from fastapi.exceptions import ResponseValidationError
# from fastapi.responses import JSONResponse
# from starlette.middleware.sessions import SessionMiddleware
# import os
#
# # Importujemy funkcję uruchomienia bazy danych i początkowych danych
# from app.core.startup import run_startup_event
# from app.services.router import router as services_router
# from app.costs.router import router as costs_router
# from app.clients.router import router as clients_router
# from app.dashboard.router import router as dashboard_router
# from app.calendar.router import router as calendar_router
# from app.reports.router import router as reports_router
# from app.auth.router import router as auth_router, get_current_user
#
# app = FastAPI()
#
# SECRET_KEY = os.getenv("SECRET_KEY", "domyslny_sekret_do_testow_lokalnych")
# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
#
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/attachments", StaticFiles(directory="attachments"), name="attachments")
# templates = Jinja2Templates(directory="templates")
#
# app.include_router(auth_router) # Router logowania - dostępny dla wszystkich
#
# # Dołączanie routerów z poszczególnych modułów
# app.include_router(services_router, dependencies=[Depends(get_current_user)])
# app.include_router(costs_router, dependencies=[Depends(get_current_user)])
# app.include_router(clients_router, dependencies=[Depends(get_current_user)])
# app.include_router(dashboard_router, dependencies=[Depends(get_current_user)])
# app.include_router(calendar_router, dependencies=[Depends(get_current_user)])
# app.include_router(reports_router, dependencies=[Depends(get_current_user)])
#
# @app.on_event("startup")
# def startup_event():
#     run_startup_event()
#
# # Główna strona, która przekierowuje do panelu
# @app.get("/", response_class=RedirectResponse, dependencies=[Depends(get_current_user)])
# async def read_root():
#     return RedirectResponse(url="/dashboard")
#
# # @app.get("/", response_class=HTMLResponse)
# # async def read_root(request: Request):
# #     return templates.TemplateResponse("index.html", {"request": request, "page_title": "Dashboard"})
# #
# # @app.get("/dashboard", response_class=HTMLResponse)
# # async def dashboard_page(request: Request):
# #     return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard"})
# #
# # @app.get("/clients", response_class=HTMLResponse)
# # async def clients_page(request: Request):
# #     return templates.TemplateResponse("clients.html", {"request": request, "title": "Klienci"})
# #
# # @app.get("/invoices", response_class=HTMLResponse)
# # async def invoices_page(request: Request):
# #     return templates.TemplateResponse("invoices.html", {"request": request, "title": "Faktury"})
# #
# # @app.get("/reports", response_class=HTMLResponse)
# # async def reports_page(request: Request):
# #     return templates.TemplateResponse("reports.html", {"request": request, "title": "Raporty"})
# #
# # @app.get("/settings", response_class=HTMLResponse)
# # async def settings_page(request: Request):
# #     return templates.TemplateResponse("settings.html", {"request": request, "title": "Ustawienia"})
# #
# # @app.exception_handler(ResponseValidationError)
# # async def response_validation_exception_handler(request, exc: ResponseValidationError):
# #     # Konwertujemy ciało błędu na string, aby uniknąć problemów z serializacją
# #     return JSONResponse(
# #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, # Używamy poprawnego kodu błędu walidacji
# #         content={
# #             "error": "Błąd walidacji odpowiedzi",
# #             "details": exc.errors(),
# #         }
# #     )


from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}