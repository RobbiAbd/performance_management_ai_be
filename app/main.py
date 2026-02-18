from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import performance, auth, motivation

app = FastAPI(title="Performance Management AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(performance.router, prefix="/api/performance", tags=["Performance"])
app.include_router(motivation.router, prefix="/api/motivation", tags=["Motivation"])
