import json
import re
from fastapi import APIRouter
from app.services.performance_service import generate_performance
from app.services.analytics_service import get_performance_analytics
from app.core.database import get_connection
from app.utils.response import success_response, error_response

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


@router.post("/generate/{employee_id}/{period}")
def generate(employee_id: int, period: str):

    result = generate_performance(employee_id, period)

    if not result:
        return error_response("KPI data not found", code=404)

    return success_response(
        data={
            "employee_id": employee_id,
            "period": period,
            "ai_summary": _parse_ai_summary_for_response(result),
        },
        message="Performance summary generated successfully",
    )


@router.get("/summary/{employee_id}/{period}")
def get_summary(employee_id: int, period: str):

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
            "employee_id": employee_id,
            "period": period,
            "ai_summary": _parse_ai_summary_for_response(result[0]),
            "generated_at": result[1],
        },
        message="Summary retrieved successfully",
    )


@router.get("/analytics/{period}")
def get_analytics(period: str):
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
