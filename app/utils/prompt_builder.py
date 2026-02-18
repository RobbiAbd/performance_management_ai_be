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
  "recommendations": ["string"],
  "motivation": "string"
}}

Keterangan:
- summary: ringkasan performa singkat (max 2 paragraf). gunakan bahasa Indonesia.
- achieved_kpi: [array] nama KPI yang mencapai/memenuhi target (contoh: ["Attendance Rate (95.00%)", "Task Completion Rate (95.00%)"]).
- not_achieved_kpi: [array] nama KPI yang belum mencapai target (contoh: ["Attendance Rate (85.00%)", "Task Completion Rate (85.00%)"]).
- recommendations: [array] berikan 2 rekomendasi konkret untuk meningkatkan performa {employee_name}. gunakan bahasa Indonesia.
- motivation: 1 kalimat kata motivasi profesional untuk {employee_name} yang bisa dijadikan sebagai motivasi untuk meningkatkan performa. gunakan bahasa Indonesia.

Aturan:
1. Jawaban HANYA berisi JSON yang valid, tanpa markdown code block atau teks tambahan.
2. Semua teks dalam bahasa Indonesia, profesional, dan sesuai data.
3. Jangan gunakan kata saya atau aku.
4. Berdasarkan data KPI: KPI tercapai jika achievement >= target yang diharapkan; belum tercapai jika di bawah target.

Data Karyawan:
Nama: {employee_name}
Periode: {period}

Data KPI:
{kpi_lines}

Output (JSON saja):
"""
