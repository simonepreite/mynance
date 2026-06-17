from fastapi import APIRouter

from app.api.routes import (
    auth,
    categorie,
    items,
    liquidita,
    login,
    movimenti,
    private,
    riepilogo,
    secchielli,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categorie.router)
api_router.include_router(liquidita.router)
api_router.include_router(movimenti.router)
api_router.include_router(secchielli.router)
api_router.include_router(riepilogo.router)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
