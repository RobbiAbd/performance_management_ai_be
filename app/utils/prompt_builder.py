def build_prompt(employee_name, kpi_data, period):
    kpi_lines = ""

    for row in kpi_data:
        kpi_lines += (
            f"- KPI: {row[1]}\n"
            f"  Target: {row[2]}\n"
            f"  Actual: {row[3]}\n"
            f"  Achievement: {row[4]}%\n\n"
        )

    return f"""
Anda adalah HR Performance Analyst profesional.

Tugas Anda: Berikan analisis performa dalam format JSON saja, tanpa teks lain sebelum atau sesudah JSON.

Struktur output JSON (wajib mengikuti format ini):
{{
  "summary": "string",
  "achieved_kpi": ["string"],
  "not_achieved_kpi": ["string"],
  "kpi_improvement_suggestions": ["string"],
  "training_rekomendation": ["string"],
  "workload_adjustment_rekomendation": ["string"],
  "motivation": "string"
}}

Keterangan:
- summary: ringkasan performa singkat (max 2 paragraf).
- achieved_kpi: [array] nama KPI yang mencapai/memenuhi target (contoh: ["Attendance Rate: target=95.00%, actual=95.00%", "Task Completion Rate: target=95.00%, actual=95.00%"]).
- not_achieved_kpi: [array] nama KPI yang belum mencapai target (contoh: ["Attendance Rate: target=95.00%, actual=85.00%", "Task Completion Rate: target=95.00%, actual=85.00%"]).
- kpi_improvement_suggestions: [array] berikan maksimal 2 rekomendasi konkret untuk meningkatkan performa KPI yang belum tercapai {employee_name}.
- training_rekomendation: [array] berikan maksimal 2 training yang dibutuhkan untuk meningkatkan performa KPI yang belum tercapai {employee_name}.
- workload_adjustment_rekomendation: [array] berikan maksimal 2 workload adjustment yang dibutuhkan untuk meningkatkan performa KPI {employee_name}.
- motivation: 1 kalimat kata motivasi profesional untuk {employee_name} yang bisa dijadikan sebagai motivasi untuk meningkatkan performa.

Aturan:
1. Jawaban HANYA berisi JSON yang valid, tanpa markdown code block atau teks tambahan.
2. Semua teks dalam bahasa Indonesia, profesional, dan sesuai data.
3. Jangan gunakan kata saya atau aku.
4. Berdasarkan data KPI: KPI tercapai jika achievement >= target yang diharapkan; belum tercapai jika di bawah target.
5. Ganti nama pada summary, recommendations, dan motivation jadi kamu.
6. Gunakan hanya bahasa Indonesia.

Data Karyawan:
Nama: {employee_name}
Periode: {period}

Data KPI:
{kpi_lines}

Output (JSON saja):
"""
