import json
import re
from app.core.database import get_connection
from app.services.ai_service import generate_ai_summary
from app.utils.prompt_builder import build_prompt
from datetime import datetime


def _extract_json_from_text(text: str) -> str | None:
    """Extract JSON string from AI output (handles markdown blocks and surrounding text)."""
    if not text or not isinstance(text, str):
        return None
    raw = text.strip()
    # Remove markdown code block
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
    raw = re.sub(r"\n?```\s*$", "", raw)
    raw = raw.strip()
    # Find first { and last } to get JSON object
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start : end + 1]
    return raw if raw.startswith("{") else None


def _parse_ai_json(ai_output: str):
    """
    Parse AI output as JSON (summary, achieved_kpi, not_achieved_kpi, recommendations, motivation).
    Returns (ai_recommendation, ai_motivation) or (None, None) if not valid JSON.
    """
    json_str = _extract_json_from_text(ai_output)
    if not json_str:
        return None, None
    # Fix common issues: trailing commas before } or ]
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)
    try:
        data = json.loads(json_str)
        rec_list = data.get("recommendations") or []
        ai_recommendation = "\n".join(rec_list) if isinstance(rec_list, list) else str(rec_list) or None
        ai_motivation = data.get("motivation") or None
        return ai_recommendation, ai_motivation
    except (json.JSONDecodeError, TypeError):
        return None, None


def _calculate_total_score(kpi_data: list) -> float:
    """Calculate average achievement percentage from KPI data."""
    if not kpi_data:
        return 0.0
    achievements = [float(row[4]) if row[4] is not None else 0.0 for row in kpi_data]
    return round(sum(achievements) / len(achievements), 2)


def _get_performance_category(total_score: float) -> str:
    """Map total_score to performance category."""
    if total_score >= 90:
        return "Excellent"
    if total_score >= 75:
        return "Good"
    if total_score >= 60:
        return "Average"
    return "Needs Improvement"


def _parse_ai_sections(ai_output: str):
    """Extract rekomendasi and motivasi sections from AI output."""
    # Find Rekomendasi section (handles **Rekomendasi** or **Recommendation**)
    rec_match = re.search(
        r"\*\*(?:Rekomendasi|Recommendation)\*\*\s*\n+(.+?)(?=\n\s*\*\*|\Z)",
        ai_output,
        re.DOTALL | re.IGNORECASE,
    )
    ai_recommendation = rec_match.group(1).strip() if rec_match else None

    # Find Motivasi section (handles **Motivasi** or **Motivation**)
    mot_match = re.search(
        r"\*\*(?:Motivasi|Motivation)\*\*\s*\n+(.+?)(?=\n\s*\*\*|\Z)",
        ai_output,
        re.DOTALL | re.IGNORECASE,
    )
    ai_motivation = mot_match.group(1).strip() if mot_match else None

    return ai_recommendation, ai_motivation


def generate_performance(employee_id: int, period: str):

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT e.full_name, k.kpi_name, a.target_value,
               r.actual_value, r.achievement_percentage
        FROM kpi_assignment a
        JOIN employees e ON e.id = a.employee_id
        JOIN kpi_master k ON k.id = a.kpi_id
        JOIN kpi_realization r ON r.assignment_id = a.id
        WHERE a.employee_id = %s AND a.period = %s
    """

    cur.execute(query, (employee_id, period))
    data = cur.fetchall()

    if not data:
        cur.close()
        conn.close()
        return None

    employee_name = data[0][0]
    prompt = build_prompt(employee_name, data, period)

    ai_output = generate_ai_summary(prompt)

    total_score = _calculate_total_score(data)
    performance_category = _get_performance_category(total_score)

    ai_recommendation, ai_motivation = _parse_ai_json(ai_output)
    if ai_recommendation is None and ai_motivation is None:
        ai_recommendation, ai_motivation = _parse_ai_sections(ai_output)

    save_query = """
        INSERT INTO performance_summary
        (employee_id, period, ai_summary, total_score, performance_category,
         ai_recommendation, ai_motivation, generated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (employee_id, period)
        DO UPDATE SET
            ai_summary = EXCLUDED.ai_summary,
            total_score = EXCLUDED.total_score,
            performance_category = EXCLUDED.performance_category,
            ai_recommendation = EXCLUDED.ai_recommendation,
            ai_motivation = EXCLUDED.ai_motivation,
            updated_at = CURRENT_TIMESTAMP
    """

    cur.execute(
        save_query,
        (
            employee_id,
            period,
            ai_output,
            total_score,
            performance_category,
            ai_recommendation,
            ai_motivation,
            datetime.now(),
        ),
    )
    conn.commit()

    cur.close()
    conn.close()

    return ai_output
