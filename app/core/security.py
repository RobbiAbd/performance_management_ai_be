from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_MAX_BYTES = 72


def _truncate_for_bcrypt(s: str) -> str:
    """Bcrypt accepts max 72 bytes. Truncate to avoid ValueError."""
    if not s:
        return s
    b = s.encode("utf-8")
    if len(b) <= BCRYPT_MAX_BYTES:
        return s
    return b[:BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if password matches bcrypt hash. False if invalid or hash malformed."""
    if not hashed_password or not hashed_password.strip():
        return False
    try:
        plain = _truncate_for_bcrypt(plain_password or "")
        return pwd_context.verify(plain, hashed_password)
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(_truncate_for_bcrypt(password or ""))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
