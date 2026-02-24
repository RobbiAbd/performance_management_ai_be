from datetime import datetime
import psycopg2
from app.core.database import get_connection
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token


def get_user_by_username(username: str) -> dict | None:
    """Get user by username. Returns dict with id, username, password_hash, full_name, email, role_id, employee_id.
    employee_id is None jika kolom belum ada di tabel users."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, username, password_hash, full_name, email, role_id, employee_id
            FROM users
            WHERE username = %s AND is_active = TRUE
            """,
            (username,),
        )
    except psycopg2.ProgrammingError:
        conn.rollback()
        cur.execute(
            """
            SELECT id, username, password_hash, full_name, email, role_id
            FROM users
            WHERE username = %s AND is_active = TRUE
            """,
            (username,),
        )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    # row bisa 7 kolom (dengan employee_id) atau 6 kolom (tanpa employee_id)
    employee_id = row[6] if len(row) > 6 else None
    return {
        "id": row[0],
        "username": row[1],
        "password_hash": row[2],
        "full_name": row[3],
        "email": row[4],
        "role_id": row[5],
        "employee_id": employee_id,
    }


def update_last_login(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET last_login = %s, updated_at = %s WHERE id = %s",
        (datetime.now(), datetime.now(), user_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def _token_payload(user: dict) -> dict:
    return {"sub": str(user["id"]), "username": user["username"], "role_id": user["role_id"]}


def _user_info(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role_id": user["role_id"],
        "employee_id": user["employee_id"],
    }


def login(username: str, password: str) -> dict | None:
    """
    Validate credentials and return token payload: { access_token, refresh_token, token_type, user }.
    Returns None if invalid.
    """
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    update_last_login(user["id"])
    data = _token_payload(user)
    access_token = create_access_token(data=data)
    refresh_token = create_refresh_token(data=data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _user_info(user),
    }


def refresh_tokens(refresh_token: str) -> dict | None:
    """
    Validasi refresh_token dan kembalikan access_token + refresh_token baru (rotation).
    Return { access_token, refresh_token, token_type, user } atau None jika invalid.
    """
    payload = decode_refresh_token(refresh_token)
    if not payload or "username" not in payload:
        return None
    user = get_user_by_username(payload["username"])
    if not user:
        return None
    data = _token_payload(user)
    return {
        "access_token": create_access_token(data=data),
        "refresh_token": create_refresh_token(data=data),
        "token_type": "bearer",
        "user": _user_info(user),
    }
