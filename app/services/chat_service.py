"""
Chatbot EP: konteks terbatas pada aplikasi Performance Management AI.
History disimpan per user di tabel chat_history.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)
from app.core.database import get_connection
from app.services.ai_service import chat_via_generate

# System prompt: batasi konteks hanya ke domain aplikasi
CHAT_SYSTEM_PROMPT = """Anda adalah asisten chatbot dari aplikasi **Performance Management AI** (EP).

Konteks yang Anda bantu HANYA seputar:
- KPI (Key Performance Indicator) dan pencapaian target
- Ringkasan performa karyawan (performance summary)
- Motivasi harian dan rekomendasi peningkatan performa
- Analytics performa (rata-rata, top performer, underperformer)
- Cara membaca/menginterpretasi hasil performa dan rekomendasi
- Jawab jika ditanya tentang seputar HCM (Human Capital Management) dan Performance Management

Aturan:
1. Jawab dalam bahasa Indonesia, sopan dan profesional.
2. Jika pertanyaan user TIDAK berkaitan dengan performa, KPI, motivasi, atau fitur aplikasi ini, tolong jelaskan dengan sopan bahwa Anda hanya dapat membantu seputar Performance Management dan arahkan user ke topik yang relevan.
3. Jangan mengada-ada data atau fitur yang tidak ada. Jika tidak tahu, sarankan untuk cek di menu aplikasi atau hubungi admin.
4. Jangan gunakan kata "saya" atau "aku"; gunakan "asisten" atau kalimat pasif.
5. Yang bertanya adalah karyawan.
6. Kamu tidak bisa memberi tahu informasi karyawan lain, hanya informasi karyawan yang bertanya.
7. JANGAN pernah menyebut "karyawan Anda"
8. JANGAN memberi insight tentang karyawan lain
9. Gunakan kata: "Anda", "performa Anda", "KPI Anda"
"""

# Jumlah pesan history terakhir (user+assistant) yang dikirim ke model (untuk konteks)
MAX_HISTORY_MESSAGES = 20


def _save_message(user_id: int, role: str, content: str) -> int:
    """Simpan satu pesan ke chat_history. Return id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_history (user_id, role, content, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (user_id, role, content, datetime.now()),
    )
    row = cur.fetchone()
    conn.commit()
    msg_id = row[0] if row else None
    cur.close()
    conn.close()
    return msg_id


def get_chat_history(user_id: int, limit: int = 50) -> list[dict]:
    """
    Ambil riwayat chat user (terbaru di akhir).
    Return list of { "id", "role", "content", "created_at" }.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, role, content, created_at
        FROM chat_history
        WHERE user_id = %s
        ORDER BY created_at ASC
        LIMIT %s
        """,
        (user_id, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "role": r[1],
            "content": r[2],
            "created_at": r[3],
        }
        for r in rows
    ]


def send_message(user_id: int, user_message: str) -> dict | None:
    """
    Simpan pesan user, panggil AI dengan konteks (system + history terbatas), simpan jawaban asisten.
    Return { "user_message_id", "assistant_message_id", "assistant_content", "created_at" } atau None jika gagal.
    """
    if not (user_message or str(user_message).strip()):
        return None

    user_message = str(user_message).strip()
    user_msg_id = _save_message(user_id, "user", user_message)
    if not user_msg_id:
        return None

    history = get_chat_history(user_id, limit=MAX_HISTORY_MESSAGES)
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})

    try:
        assistant_content = chat_via_generate(messages)
    except Exception as e:
        logger.warning("Chat (generate) failed: %s", e, exc_info=True)
        assistant_content = "Maaf, terjadi gangguan saat memproses. Silakan coba lagi."

    assistant_content = (assistant_content or "").strip() or "Maaf, saya tidak dapat menghasilkan jawaban."
    assistant_msg_id = _save_message(user_id, "assistant", assistant_content)

    return {
        "user_message_id": user_msg_id,
        "assistant_message_id": assistant_msg_id,
        "assistant_content": assistant_content,
        "created_at": datetime.now().isoformat(),
    }
