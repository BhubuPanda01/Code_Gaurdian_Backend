# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
# from app.db.session import engine
# from app.db.models import Base  

# from app.api.routes.v1 import auth_routes

# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# def create_app() -> FastAPI:
#     app = FastAPI(
#         title="Code Guardian Backend",
#         version="0.1.0",
#     )

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],  # allow all for development
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )


#     @app.on_event("startup")
#     async def startup_event():
#         await init_db()


#     app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])

#     return app



# print(settings.DATABASE_URL)  # Debugging line to check if settings are loaded correctly

# app = create_app()






from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.models import Base
from app.api.routes.v1 import auth_routes


async def init_db():
    """
    Create database tables if they do not exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Code Guardian Backend",
        version="0.1.0",
    )

    # -----------------------------
    # CORS Middleware
    # -----------------------------
    cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------
    # Startup Event
    # -----------------------------
    @app.on_event("startup")
    async def startup_event():
        await init_db()

    # -----------------------------
    # Routers
    # -----------------------------
    app.include_router(
        auth_routes.router,
        prefix="/api/v1/auth",
        tags=["auth"],
    )

    return app


# Create FastAPI application instance
app = create_app()