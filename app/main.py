from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.v1 import auth_routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="Code Guardian Backend",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # allow all for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])

    return app


app = create_app()
