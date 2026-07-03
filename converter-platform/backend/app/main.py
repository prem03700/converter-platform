import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.router import api_router
from app.config import settings
from app.converters.base import ConversionError
from app.database import Base, engine
from app.utils.validation import FileValidationError

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger("converter_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # NOTE: this create_all is a development convenience only. In
    # production, schema changes must go through Alembic migrations
    # (see /backend/alembic), never through create_all.
    if settings.ENV == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Development mode: tables created/verified via create_all.")
    yield


limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    description="A modular, AI-assisted file conversion platform.",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FileValidationError)
async def file_validation_handler(request: Request, exc: FileValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(ConversionError)
async def conversion_error_handler(request: Request, exc: ConversionError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
