from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.services.auth_service import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=True)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode JWT and return current user from DB (id, username, employee_id, ...)."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_username(payload.get("username", ""))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_with_employee(token: str = Depends(oauth2_scheme)) -> dict:
    """Same as get_current_user but requires employee_id (for performance generate/summary)."""
    user = get_current_user(token)
    if user.get("employee_id") is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not linked to an employee. Contact admin.",
        )
    return user
