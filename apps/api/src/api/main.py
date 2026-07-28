from fastapi import FastAPI

app = FastAPI(
    title="OnboardAI API",
    description="Enterprise Autonomous Customer Onboarding & Integration Platform",
    version="0.1.0",
)


@app.get("/healthz")
async def health() -> dict[str, str]:
    return {"status": "ok"}
