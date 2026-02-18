"""Analytics service for Decision Support System."""

from app.core.database import get_connection


def get_performance_analytics(period: str) -> dict | None:
    """
    Get analytics for Decision Support System:
    - Average score per department
    - Top performers
    - Underperformers
    - Category distribution
    """
    conn = get_connection()
    cur = conn.cursor()

    # 1. Rata-rata skor per departemen
    # Assumes: employees.department_id, departments(id, name)
    try:
        cur.execute("""
            SELECT COALESCE(d.name, 'Unassigned') AS department_name,
                   ROUND(AVG(ps.total_score)::numeric, 2) AS avg_score,
                   COUNT(ps.employee_id) AS employee_count
            FROM performance_summary ps
            JOIN employees e ON e.id = ps.employee_id
            LEFT JOIN departments d ON d.id = e.department_id
            WHERE ps.period = %s AND ps.total_score IS NOT NULL
            GROUP BY d.id, d.name
            ORDER BY avg_score DESC
        """, (period,))
        avg_per_department = [
            {"department": row[0], "avg_score": float(row[1]), "employee_count": row[2]}
            for row in cur.fetchall()
        ]
    except Exception:
        conn.rollback()
        # Fallback: overall average if departments table/column doesn't exist
        cur.execute("""
            SELECT 'All Employees' AS department_name,
                   ROUND(AVG(total_score)::numeric, 2) AS avg_score,
                   COUNT(employee_id) AS employee_count
            FROM performance_summary
            WHERE period = %s AND total_score IS NOT NULL
        """, (period,))
        row = cur.fetchone()
        avg_per_department = [
            {"department": row[0], "avg_score": float(row[1]), "employee_count": row[2]}
        ] if row and row[1] else []

    # 2. Top performer (top 5 by total_score)
    cur.execute("""
        SELECT e.id, e.employee_code, e.full_name, ps.total_score, ps.performance_category
        FROM performance_summary ps
        JOIN employees e ON e.id = ps.employee_id
        WHERE ps.period = %s AND ps.total_score IS NOT NULL
        ORDER BY ps.total_score DESC
        LIMIT 5
    """, (period,))
    top_performers = [
        {
            "employee_id": row[0],
            "employee_code": row[1] or "",
            "full_name": row[2],
            "total_score": float(row[3]) if row[3] else 0,
            "performance_category": row[4] or "N/A",
        }
        for row in cur.fetchall()
    ]

    # 3. Underperformer (bottom 5 by total_score)
    cur.execute("""
        SELECT e.id, e.employee_code, e.full_name, ps.total_score, ps.performance_category
        FROM performance_summary ps
        JOIN employees e ON e.id = ps.employee_id
        WHERE ps.period = %s AND ps.total_score IS NOT NULL
        ORDER BY ps.total_score ASC
        LIMIT 5
    """, (period,))
    underperformers = [
        {
            "employee_id": row[0],
            "employee_code": row[1] or "",
            "full_name": row[2],
            "total_score": float(row[3]) if row[3] else 0,
            "performance_category": row[4] or "N/A",
        }
        for row in cur.fetchall()
    ]

    # 4. Distribusi kategori
    cur.execute("""
        SELECT performance_category, COUNT(*) AS count
        FROM performance_summary
        WHERE period = %s AND performance_category IS NOT NULL
        GROUP BY performance_category
        ORDER BY count DESC
    """, (period,))
    category_distribution = [
        {"category": row[0], "count": row[1]}
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return {
        "period": period,
        "avg_score_per_department": avg_per_department,
        "top_performers": top_performers,
        "underperformers": underperformers,
        "category_distribution": category_distribution,
    }
