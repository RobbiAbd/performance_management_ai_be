from datetime import datetime
from app.core.database import get_connection
from app.services.ai_service import generate_ai_summary

# Advisory lock ID: satu motivasi per hari, cegah insert 2x saat request bersamaan
_MOTIVATION_DAILY_LOCK_ID = 0x6D6F7469  # "moti" in hex


MOTIVATION_PROMPT = """Anda adalah motivator profesional. Tulis satu kalimat motivasi singkat untuk hari ini (max 2 kalimat). Bahasa Indonesia. Tanpa tanda kutip atau prefix. Langsung kalimat motivasinya saja."""


def generate_daily_motivation() -> dict | None:
    """
    Generate motivasi harian via AI dan simpan ke tabel motivation.
    Jika hari ini (tanggal created_at) sudah ada row, kembalikan yang ada tanpa insert baru.
    Pakai advisory lock supaya dua request bersamaan tidak insert 2x di tanggal sama.
    Returns dict dengan id, motivation, created_at atau None jika gagal.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Lock: hanya satu proses yang boleh cek + insert untuk hari ini
    cur.execute("SELECT pg_advisory_xact_lock(%s)", (_MOTIVATION_DAILY_LOCK_ID,))

    cur.execute(
        """
        SELECT id, motivation, created_at
        FROM motivation
        WHERE DATE(created_at) = CURRENT_DATE
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    existing = cur.fetchone()
    if existing:
        conn.rollback()
        cur.close()
        conn.close()
        return {
            "id": existing[0],
            "motivation": existing[1],
            "created_at": existing[2],
        }

    text = generate_ai_summary(MOTIVATION_PROMPT)
    if not text or not text.strip():
        conn.rollback()
        cur.close()
        conn.close()
        return None
    motivation = text.strip().strip('"').strip("'")

    cur.execute(
        "INSERT INTO motivation (motivation, created_at) VALUES (%s, %s) RETURNING id, motivation, created_at",
        (motivation, datetime.now()),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "motivation": row[1],
        "created_at": row[2],
    }
