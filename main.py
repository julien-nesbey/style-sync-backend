from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from api import analytics_router, image_router, weather_router
from api.auth import router as auth_router
from api.closet import router as closet_router

# Create database tables
Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    """Application factory used by uvicorn and tests."""

    app = FastAPI(
        title="Style-Sync Engine",
        description=(
            "Async AI wardrobe backend for image intelligence, weather orchestration, "
            "and sustainability analytics."
        ),
        version="0.1.0",
    )

    # Add CORS middleware to allow frontend requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(image_router)
    app.include_router(weather_router)
    app.include_router(analytics_router)
    app.include_router(auth_router)
    app.include_router(closet_router)

    from fastapi import Request, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        import json
        with open("422_dump.json", "w") as f:
            json.dump({"errors": exc.errors(), "headers": dict(request.headers)}, f, default=str)
        print("====== 422 VALIDATION FAILED ======")
        print("Errors:", exc.errors())
        # DO NOT DO await request.form() because it consumes body
        # but we can print headers
        print("Headers:", request.headers)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "body": str(exc.body)},
        )

    @app.get("/health", tags=["meta"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
