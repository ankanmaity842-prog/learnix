from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

from app.api.auth import router as auth_router
from app.api.google import router as google_router
from app.api.search import router as search_router
from app.api.videoes import router as videos_router
from app.api.recommendations import router as recommendations_router
from app.api.learning import router as learning_router
from app.api.notes import router as notes_router
from app.api.quiz import router as quiz_router
from app.api.progress import router as progress_router
from app.api.knowledge import router as knowledge_router
from app.api.vision import router as vision_router
from app.api.language import router as languages_router


setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    search_router,
    prefix="/api",
)

app.include_router(
    videos_router,
    prefix="/api",
)

app.include_router(
    recommendations_router,
    prefix="/api",
)

app.include_router(
    learning_router,
    prefix="/api",
)

app.include_router(
    notes_router,
    prefix="/api",
)

app.include_router(
    quiz_router,
    prefix="/api",
)

app.include_router(
    progress_router,
    prefix="/api",
)

app.include_router(
    knowledge_router,
    prefix="/api",
)

app.include_router(
    vision_router,
    prefix="/api",
)

app.include_router(
    languages_router,
    prefix="/api",
)

app.include_router(
    google_router,
    prefix="/api",
)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }