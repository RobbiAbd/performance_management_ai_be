from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.services.auth_service import login
from app.utils.response import success_response, error_response

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def auth_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login (form, untuk Swagger). Mengembalikan access_token (JWT).
    Header: Authorization: Bearer <token>
    """
    result = login(form_data.username, form_data.password)
    if not result:
        return error_response("Invalid username or password", code=401)
    return success_response(data=result, message="Login successful")


@router.post("/login/json")
def auth_login_json(body: LoginRequest):
    """
    Login dengan JSON body: { "username": "...", "password": "..." }.
    Mengembalikan access_token (JWT). Header: Authorization: Bearer <token>
    """
    result = login(body.username, body.password)
    if not result:
        return error_response("Invalid username or password", code=401)
    return success_response(data=result, message="Login successful")
