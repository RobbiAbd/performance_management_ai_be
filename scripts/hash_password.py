"""Generate bcrypt hash untuk kolom password_hash di tabel users."""
import sys
import os

# Supaya bisa import app dari project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/hash_password.py <password>")
        sys.exit(1)
    password = sys.argv[1]
    print(get_password_hash(password))
