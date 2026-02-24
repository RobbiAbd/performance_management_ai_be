from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.routes import performance, auth, motivation, chat
from app.utils.response import error_response

app = FastAPI(title="Performance Management AI")


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    """Error dari HTTPException (401, 403, 404, dll) → format standar."""
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    body = error_response(message=detail, code=exc.status_code, data=None)
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Error validasi (422) → format standar."""
    body = error_response(message="Validasi gagal", code=422, data=exc.errors())
    return JSONResponse(status_code=422, content=body)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "API is running"}

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(performance.router, prefix="/api/performance", tags=["Performance"])
app.include_router(motivation.router, prefix="/api/motivation", tags=["Motivation"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
