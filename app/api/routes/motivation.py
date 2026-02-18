from fastapi import APIRouter, Depends
from app.services.motivation_service import generate_daily_motivation
from app.utils.response import success_response, error_response
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/generate")
def generate_motivation(current_user: dict = Depends(get_current_user)):
    """
    Generate motivasi harian via AI dan simpan ke tabel motivation.
    Memerlukan token (Authorization: Bearer <token>).
    """
    result = generate_daily_motivation()
    if not result:
        return error_response("Gagal generate motivasi", code=500)
    return success_response(
        data=result,
        message="Motivasi harian berhasil digenerate",
    )
