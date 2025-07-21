# utils.py
import matplotlib.pyplot as plt
import io
import urllib, base64
from datetime import datetime, timedelta

def generate_task_pie_chart(task_dict):
    labels = []
    sizes = []

    for task, durations in task_dict.items():
        total_minutes = sum([d.total_seconds() for d in durations]) / 60
        if total_minutes > 0:
            labels.append(task)
            sizes.append(total_minutes)

    if not labels:
        return None  # グラフがないときはNone

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    chart = base64.b64encode(image_png).decode('utf-8')
    return chart

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, "%H:%M").time()
    except (ValueError, TypeError):
        return None

def generate_monthly_comparison(current_summary, compare_summary):
    total_diff = current_summary['total'] - compare_summary['total']
    avg_diff = current_summary['average'] - compare_summary['average']
    count_diff = current_summary['count'] - compare_summary['count']

    total_rate = round((total_diff.total_seconds() / compare_summary['total'].total_seconds()) * 100, 1) if compare_summary['total'].total_seconds() else 0
    avg_rate = round((avg_diff.total_seconds() / compare_summary['average'].total_seconds()) * 100, 1) if compare_summary['average'].total_seconds() else 0
    count_rate = round((count_diff / compare_summary['count']) * 100, 1) if compare_summary['count'] else 0

    return {
        'diff_total': f"{'+' if total_diff.total_seconds() >= 0 else ''}{format_timedelta(total_diff)}",
        'rate_total': f"{'+' if total_rate >= 0 else ''}{total_rate}%",
        'diff_avg': f"{'+' if avg_diff.total_seconds() >= 0 else ''}{format_timedelta(avg_diff)}",
        'rate_avg': f"{'+' if avg_rate >= 0 else ''}{avg_rate}%",
        'diff_count': f"{'+' if count_diff >= 0 else ''}{count_diff}件",
        'rate_count': f"{'+' if count_rate >= 0 else ''}{count_rate}%",
    }

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60
    return f"{hours}時間{minutes}分"

def summarize_reports(reports):
    durations = [r.作業時間 for r in reports if r.作業時間]
    total = sum(durations, timedelta()) if durations else timedelta()
    average = total / len(durations) if durations else timedelta()
    count = len(durations)
    return {
        'total': total,       # timedelta のまま
        'average': average,   # timedelta のまま
        'count': count        # 数値のまま
    }
