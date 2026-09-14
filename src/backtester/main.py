from fastapi import FastAPI

from backtester.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Distributed Backtester",
    description="An incremental distributed backtesting system.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}

