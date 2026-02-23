from __future__ import annotations

import warnings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_router
from app.core.config import get_settings
from app.core.logging_config import get_logger, setup_logging

warnings.filterwarnings("ignore", category=UserWarning)

settings = get_settings()
setup_logging(settings.log_file, settings.log_level)
logger = get_logger(__name__)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    logger.debug("Health check invoked")
    return {
        "status": "success",
        "message": f"{settings.app_name} is running",
        "environment": settings.environment,
    }


app.include_router(api_router)
