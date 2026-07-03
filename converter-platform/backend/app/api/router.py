from fastapi import APIRouter

from app.api.routes import admin, ai, auth, convert, history, upload, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(upload.router)
api_router.include_router(convert.router)
api_router.include_router(history.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)
