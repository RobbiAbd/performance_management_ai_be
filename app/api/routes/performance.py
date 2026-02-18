import json
import re
from fastapi import APIRouter, Depends
from app.services.performance_service import generate_performance, get_employee_code_by_id
from app.services.analytics_service import get_performance_analytics
from app.core.database import get_connection
from app.utils.response import success_response, error_response
from app.api.dependencies import get_current_user, get_current_user_with_employee

router = APIRouter()


def _parse_ai_summary_for_response(ai_summary):
    """Return ai_summary as object if valid JSON, else as string."""
    if not ai_summary or not isinstance(ai_summary, str):
        return ai_summary
    raw = ai_summary.strip().replace("\r\n", "\n").replace("\r", "\n")
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
    raw = re.sub(r"\n?```\s*$", "", raw)
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end > start:
        raw = raw[start : end + 1]
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    if raw.rstrip() and not raw.rstrip().endswith("}"):
        try:
            return json.loads(raw + "}")
        except json.JSONDecodeError:
            pass
    return ai_summary


@router.post("/generate/{period}")
def generate(period: str, current_user: dict = Depends(get_current_user_with_employee)):

    employee_code = get_employee_code_by_id(current_user["employee_id"])
    if not employee_code:
        return error_response("Employee not found for this user", code=404)

    result = generate_performance(employee_code, period)

    if not result:
        return error_response("KPI data not found", code=404)

    return success_response(
        data={
            "employee_code": employee_code,
            "period": period,
            "ai_summary": _parse_ai_summary_for_response(result),
        },
        message="Performance summary generated successfully",
    )


@router.get("/summary/me/{period}")
def get_summary(period: str, current_user: dict = Depends(get_current_user_with_employee)):

    employee_id = current_user["employee_id"]
    employee_code = get_employee_code_by_id(employee_id)
    if not employee_code:
        return error_response("Employee not found for this user", code=404)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ai_summary, generated_at
        FROM performance_summary
        WHERE employee_id = %s AND period = %s
    """, (employee_id, period))

    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return error_response("Summary not found", code=404)

    return success_response(
        data={
            "employee_code": employee_code,
            "period": period,
            "ai_summary": _parse_ai_summary_for_response(result[0]),
            "generated_at": result[1],
        },
        message="Summary retrieved successfully",
    )


@router.get("/analytics/{period}")
def get_analytics(period: str, current_user: dict = Depends(get_current_user)):
    """
    Decision Support System: Analytics untuk periode tertentu.
    - Rata-rata skor per departemen
    - Top performer
    - Underperformer
    - Distribusi kategori performa
    """
    result = get_performance_analytics(period)
    return success_response(
        data=result,
        message="Analytics retrieved successfully",
    )
