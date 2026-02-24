from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.services.auth_service import login, refresh_tokens
from app.utils.response import success_response, error_response

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
def auth_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login (form, untuk Swagger). Mengembalikan access_token, refresh_token, dan user.
    Header: Authorization: Bearer <access_token>
    """
    result = login(form_data.username, form_data.password)
    if not result:
        return error_response("Invalid username or password", code=401)
    return success_response(data=result, message="Login successful")


@router.post("/login/json")
def auth_login_json(body: LoginRequest):
    """
    Login dengan JSON body: { "username": "...", "password": "..." }.
    Mengembalikan access_token, refresh_token, dan user. Header: Authorization: Bearer <access_token>
    """
    result = login(body.username, body.password)
    if not result:
        return error_response("Invalid username or password", code=401)
    return success_response(data=result, message="Login successful")


@router.post("/refresh")
def auth_refresh(body: RefreshRequest):
    """
    Tukar refresh_token dengan access_token dan refresh_token baru (rotation).
    Body: { "refresh_token": "..." }. Tidak perlu Authorization header.
    """
    result = refresh_tokens(body.refresh_token)
    if not result:
        return error_response("Invalid or expired refresh token", code=401)
    return success_response(data=result, message="Token renewed successfully")
