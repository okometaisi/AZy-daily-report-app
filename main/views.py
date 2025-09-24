from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.db.models import Count

from datetime import datetime, timedelta
from collections import defaultdict

from .models import DailyReport, Task, TaskPreset
from .utils import parse_time, format_timedelta
from main.utils import summarize_reports, generate_monthly_comparison

from django.db.models import F

import re

def jsw_product_sort_key(product_name, company_name):
    """
    商品名にJSWの番号があれば数値として取得。
    ただし『日本製鋼所』のときのみ考慮。それ以外の会社は普通にソート。
    """
    if company_name != '日本製鋼所':
        return float('inf')  # 他の会社では数字順は無視（後ろに行く）
    
    match = re.search(r'JSW(\d+)', product_name)
    if match:
        return int(match.group(1))
    return float('inf')



# 選択肢データ
COMPANY_CHOICES = [
    'トーヨーエイテック',
    '日本製鋼所',
    '長浜製作所',
    '富士機械',
    '自社',
    'コンテナ',
    'その他',
    
    
]

PRODUCT_CHOICES = [
    'シェル',
    'リアホルダーLR',
    'レセプタクル',
    'ブロックLR',
    'Vブロック',
    'テーブル900',
    'テンションベース',
    'ボディKD',
    'ボディHP',
    'ボディHBX',
    'ボディTWI',
    'インディックス',
    'ベッドL＝1000',
    'ベッドL＝1500',
    'ベッドL＝2000',
    'ベッドL＝2500',
    'ベッドL＝3000',
    'ベッドL＝2000（両端面加工）',
    'ジョウブフレーム',
    'インアウトフィードフレーム',
    'フィードフレーム',
    'フレーム',
    'JSW100大物',
    'JSW100小物',
    'JSW130大物',
    'JSW130小物',
    'JSW180大物',
    'JSW180小物',
    '1300クロスリンク',
    '1300タンリンク',
    '220ｔカドウバンウエ',
    '220ｔカドウバンシタ',
    '220ｔコテイバン',
    'JT70カドウバンウエ',
    'JT70カドウバンシタ',
    'JT70カコテイバン',
    'JSW素材',
    '自社トラック積み込み',
    'コンテナ積み荷おろし',
    'JSW100出荷',
    'JSW130出荷',
    'JSW180出荷',
    'ターンテーブル',
    '事務',
    'その他',
]

def generate_time_choices():
    times = []
    current = datetime.strptime("05:30", "%H:%M")
    end = datetime.strptime("23:59", "%H:%M")
    while current <= end:
        times.append(current.strftime("%H:%M"))
        current += timedelta(minutes=5)
    return times

TIME_CHOICES = generate_time_choices()

def format_duration_data(group_dict):
    result = []
    for key, durations in group_dict.items():
        total = sum(durations, timedelta())
        avg = total / len(durations)

        total_minutes = int(total.total_seconds() // 60)
        avg_minutes = int(avg.total_seconds() // 60)

        result.append({
            'company': key[0] if isinstance(key, tuple) else '',
            'product': key[1] if isinstance(key, tuple) else '',
            'task': key if isinstance(key, str) else '',
            'total_duration_hour': total_minutes // 60,
            'total_duration_minute': total_minutes % 60,
            'avg_duration_hour': avg_minutes // 60,
            'avg_duration_minute': avg_minutes % 60,
            'count': len(durations),
        })

    # ✅ 並び替えをここで実行！
    result.sort(key=lambda x: (
        x.get('company', ''),
        jsw_product_sort_key(x.get('product', ''), x.get('company', '')),
        x.get('product', '')  # 商品名アルファベット順の保険
    ))


    return result



def home(request):
    return render(request, 'home.html')

# ② report_input（置き換え）
def report_input(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        company = request.POST.get('company')
        product = request.POST.get('product')
        task_text = request.POST.get('task')  # 既存の手入力も保持
        start_time = parse_time(request.POST.get('start_time'))
        end_time = parse_time(request.POST.get('end_time'))
        memo = request.POST.get('memo')

        # 追加：選択式（task_fk）
        task_fk_id = request.POST.get('task_fk')
        task_fk = Task.objects.filter(id=task_fk_id).first() if task_fk_id else None

        # 作業時間の自動計算
        if start_time and end_time:
            start_dt = datetime.combine(datetime.today(), start_time)
            end_dt = datetime.combine(datetime.today(), end_time)
            duration = end_dt - start_dt if end_dt > start_dt else None
        else:
            duration = None

        # 保存（選択があれば旧textにも反映しておくと表示が揃って便利）
        DailyReport.objects.create(
            date=date,
            company=company,
            product=product,
            task=(task_fk.name if task_fk else task_text),
            task_fk=task_fk,
            start_time=start_time,
            end_time=end_time,
            memo=memo,
            作業時間=duration
        )
        return redirect('home')

    context = {
        'company_choices': COMPANY_CHOICES,
        'product_choices': PRODUCT_CHOICES,
        'time_choices': TIME_CHOICES,
        'tasks': Task.objects.all().order_by('name'),  # プルダウン用
        'presets': TaskPreset.objects.filter(is_active=True).order_by('sort_order', 'label'),
    }
    return render(request, 'report_input.html', context)



# ③ report_edit（置き換え）
def report_edit(request, report_id):
    report = get_object_or_404(DailyReport, pk=report_id)

    if request.method == 'POST':
        date_input = request.POST.get('date')
        if not date_input:
            return HttpResponseBadRequest("日付が入力されていません。")
        try:
            report.date = datetime.strptime(date_input.replace('/', '-'), "%Y-%m-%d").date()
        except ValueError:
            return HttpResponseBadRequest("日付の形式が正しくありません。")

        report.company = request.POST.get('company')
        report.product = request.POST.get('product')
        # 既存のテキスト入力
        task_text = request.POST.get('task')

        # 追加：選択式（task_fk）
        task_fk_id = request.POST.get('task_fk')
        report.task_fk = Task.objects.filter(id=task_fk_id).first() if task_fk_id else None

        # 同期：選択があれば task（文字列）も合わせる
        report.task = report.task_fk.name if report.task_fk else task_text

        report.start_time = parse_time(request.POST.get('start_time'))
        report.end_time = parse_time(request.POST.get('end_time'))
        report.memo = request.POST.get('memo')

        # 作業時間の再計算
        if report.start_time and report.end_time:
            start = datetime.combine(datetime.today(), report.start_time)
            end = datetime.combine(datetime.today(), report.end_time)
            report.作業時間 = end - start
        else:
            report.作業時間 = None

        report.save()

        # 編集後も同じ月へ戻る処理（元のロジックのまま）
        year = request.GET.get('year')
        month = request.GET.get('month')
        if year and month:
            return redirect(f'/report/list/?year={year}&month={month}')
        return redirect('report_list')

    context = {
        'report': report,
        'company_choices': COMPANY_CHOICES,
        'product_choices': PRODUCT_CHOICES,
        'time_choices': TIME_CHOICES,
        'tasks': Task.objects.all().order_by('name'),  # プルダウン用
        'presets': TaskPreset.objects.filter(is_active=True).order_by('sort_order', 'label'),
    }
    return render(request, 'report_edit.html', context)

def report_list(request):
    years = list(range(2023, 2027))
    months = list(range(1, 13))
    days = list(range(1, 32))  # 日付フィルタ用

    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    selected_day = request.GET.get('day')

    if selected_year and selected_month:
        qs = DailyReport.objects.filter(date__year=selected_year, date__month=selected_month)
        if selected_day:
            qs = qs.filter(date__day=selected_day)
        reports = qs.order_by('date', F('start_time').asc(nulls_last=True), 'id')

    else:
        today = datetime.today()
        selected_year = today.year
        selected_month = today.month
        selected_day = None
        reports = (DailyReport.objects
                   .filter(date__year=selected_year, date__month=selected_month)
                   .order_by('date', F('start_time').asc(nulls_last=True), 'id'))

    context = {
        'years': years,
        'months': months,
        'days': days,
        'selected_year': int(selected_year),
        'selected_month': int(selected_month),
        'selected_day': int(selected_day) if selected_day else None,
        'reports': reports,
    }
    return render(request, 'report_list.html', context)





def report_delete(request, report_id):
    report = get_object_or_404(DailyReport, pk=report_id)
    report.delete()

    # 年月のクエリパラメータを取得
    year = request.GET.get('year')
    month = request.GET.get('month')

    # 年月がある場合はその年月へリダイレクト、なければ今月
    if year and month:
        return redirect(f'/report/list/?year={year}&month={month}')
    else:
        return redirect('report_list')


from .utils import generate_monthly_comparison, summarize_reports

def report_summary(request):
    selected_year = int(request.GET.get('year', datetime.now().year))
    selected_month = int(request.GET.get('month', datetime.now().month))
    
    compare_year = int(request.GET.get('compare_year', selected_year))
    compare_month = int(request.GET.get('compare_month', selected_month))
    
    return redirect(f'/report/comparison/?compare_year={selected_year}&compare_month={selected_month}')

 
    # 今月のレポートを取得
    reports = DailyReport.objects.filter(date__year=selected_year, date__month=selected_month)

    # 集計用ディクショナリ
    summary_dict = defaultdict(list)
    task_dict = defaultdict(list)

    for report in reports:
        if not report.作業時間:
            continue
        summary_dict[(report.company, report.product)].append(report.作業時間)
        task_dict[report.task].append(report.作業時間)

    # 集計結果を整形
    summary_data = format_duration_data(summary_dict)
    task_data = format_duration_data(task_dict)
    
    # ✅ 作業内容を50音順にソート！
    task_data.sort(key=lambda x: x['task'])

    # 🧠 今月の集計まとめ
    current_summary = summarize_reports(reports)

    # 📅 比較する月（前月）を自動で決める
    if selected_month == 1:
        compare_year = selected_year - 1
        compare_month = 12
    else:
        compare_year = selected_year
        compare_month = selected_month - 1

    compare_reports = DailyReport.objects.filter(date__year=compare_year, date__month=compare_month)
    compare_summary = summarize_reports(compare_reports)

    # ✅ 差分・率を計算！
    comparison = generate_monthly_comparison(current_summary, compare_summary)

    context = {
        'selected_year': selected_year,
        'selected_month': selected_month,
        'summary_data': summary_data,
        'task_data': task_data,
        'comparison': comparison,
        'years': list(range(2025, 2041)),
        'months': list(range(1, 13)),
        'compare_year': compare_year,
        'compare_month': compare_month,
        'current_total': format_timedelta(current_summary['total']),
        'current_average': format_timedelta(current_summary['average']),
        'compare_total': format_timedelta(compare_summary['total']),
        'compare_average': format_timedelta(compare_summary['average']),
    }

    return render(request, 'report_summary.html', context)



# ↓ 時間を「2時間30分」みたいに整形するヘルパー関数
def format_duration(duration):
    total_minutes = int(duration.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}時間{minutes}分"

def report_comparison(request):
    from collections import defaultdict
    from datetime import datetime, timedelta

    # ✅ 今月（selected_○○）
    selected_year = int(request.GET.get('target_year') or request.GET.get('selected_year') or datetime.now().year)
    selected_month = int(request.GET.get('target_month') or request.GET.get('selected_month') or datetime.now().month)

    
    compare_year = int(request.GET.get('compare_year', selected_year))
    compare_month = int(request.GET.get('compare_month', selected_month - 1 or 12))


    current_reports = DailyReport.objects.filter(
        date__year=selected_year, date__month=selected_month
    )

    # ✅ 集計用
    summary_dict = defaultdict(list)
    task_dict = defaultdict(list)

    for report in current_reports:
        if report.作業時間:
            summary_dict[(report.company, report.product)].append(report.作業時間)
            task_dict[report.task].append(report.作業時間)

    summary_data = format_duration_data(summary_dict)
    task_data = format_duration_data(task_dict)
    task_data.sort(key=lambda x: x['task'])
    current_summary = summarize_reports(current_reports)

    # ✅ 比較月（compare_○○）
    compare_year = int(request.GET.get('compare_year', selected_year))
    compare_month = int(request.GET.get('compare_month', selected_month - 1 or 12))
    if selected_month == 1:
        compare_year = selected_year - 1
        compare_month = 12

    compare_reports = DailyReport.objects.filter(
        date__year=compare_year, date__month=compare_month
    )
    compare_summary = summarize_reports(compare_reports)
    
    
    print("DEBUG: current total =", current_summary['total'])
    print("DEBUG: current average =", current_summary['average'])
    print("DEBUG: compare total =", compare_summary['total'])
    print("DEBUG: compare average =", compare_summary['average'])
    
    

    # ✅ 差分・率を出す
    comparison = generate_monthly_comparison(current_summary, compare_summary)

    context = {
        'selected_year': selected_year,
        'selected_month': selected_month,
        'compare_year': compare_year,
        'compare_month': compare_month,
        'comparison': comparison,
        'summary_data': summary_data,
        'task_data': task_data,
        'years': list(range(2025, 2041)),
        'months': list(range(1, 13)),
        'current': current_summary,
        'compare': compare_summary,
        
        'current_total': format_timedelta(current_summary['total']),
        'current_average': format_timedelta(current_summary['average']),
        'compare_total': format_timedelta(compare_summary['total']),
        'compare_average': format_timedelta(compare_summary['average']),
    }

    
    print("=== DEBUG: comparison.current ===")
    print(comparison.get("current")) 
    print("=== DEBUG: comparison ===")
    print(comparison)

    print("=== DEBUG: comparison.current ===")
    print(comparison.get("current"))
    print("=== comparison の型 ===")
    print(type(comparison))

    print("=== comparison の中身 ===")
    print(comparison)
    
    return render(request, 'report_comparison.html', context)



