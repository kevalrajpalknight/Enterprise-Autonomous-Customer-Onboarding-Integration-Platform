from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OnboardAI Enterprise API",
    description="Automated customer onboarding and integration platform.",
    version="1.0.0",
)

# Standard permissive CORS for local development (lock down for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Docker container health check endpoint.
    """
    return {"status": "healthy", "service": "api"}


# TODO: Include routers for /v1/documents, /v1/workflows, etc.
