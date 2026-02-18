from fastapi import FastAPI
from app.api.routes import performance

app = FastAPI(title="Performance Management AI")

app.include_router(performance.router, prefix="/performance", tags=["Performance"])
