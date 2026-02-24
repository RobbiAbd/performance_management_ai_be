from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.dependencies import get_current_user
from app.services.chat_service import send_message, get_chat_history
from app.utils.response import success_response, error_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(body: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Kirim pesan ke chatbot EP. Konteks chatbot terbatas pada aplikasi
    Performance Management (KPI, performa, motivasi, rekomendasi).
    History disimpan per user. Memerlukan token (Authorization: Bearer <token>).
    """
    if not body.message or not str(body.message).strip():
        return error_response("Pesan tidak boleh kosong", code=400)

    result = send_message(current_user["id"], body.message.strip())
    if not result:
        return error_response("Gagal memproses chat", code=500)

    return success_response(
        data={
            "user_message_id": result["user_message_id"],
            "assistant_message_id": result["assistant_message_id"],
            "assistant_content": result["assistant_content"],
            "created_at": result["created_at"],
        },
        message="Chat berhasil",
    )


@router.get("/chat/history")
def chat_history(limit: int = 50, current_user: dict = Depends(get_current_user)):
    """
    Ambil riwayat chat user yang login. Opsional: limit (default 50).
    Memerlukan token (Authorization: Bearer <token>).
    """
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    history = get_chat_history(current_user["id"], limit=limit)
    return success_response(
        data={"history": history, "count": len(history)},
        message="Riwayat chat berhasil diambil",
    )
