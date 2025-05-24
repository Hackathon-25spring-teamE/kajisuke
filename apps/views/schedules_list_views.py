from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q, Prefetch
from datetime import datetime, date
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
from ..models import PastSchedule, Schedule, ExceptionalSchedule, CompletedSchedule
from ..utils.calendar_utils import get_reccureced_dates, get_japanese_holidays, wareki


# 登録しているスケジュール一覧
@login_required
def schedules_list(request):
    # schedulesから対象ユーザーのis_active=trueとなっているレコードを全て取得する
    schedules = Schedule.objects.filter(
            user=request.user, 
            is_active=True,
        ).select_related(
            'task__task_category'
        ).order_by('start_date')
    
    schedules_list = []

    for item in schedules:
        frequency_or_date = ""

        # frequency == "NONE"の場合→start_dateを表示
        if item.frequency == "NONE":
            frequency_or_date = f"{item.start_date.year}年{item.start_date.month}月{item.start_date.day}日"

        elif item.frequency == "DAILY":
            if item.interval == 1:
                interval = "毎日"
            else:
                interval = f"{item.interval}日毎"
            rule = ""

        elif item.frequency == "WEEKLY":
            if item.interval == 1:
                interval = "毎週"
            else:
                interval = f"{item.interval}週毎"
            rule = weekday_dict.get(item.day_of_week)




        frequency_or_date = f"{interval} {rule}"

        schedule = {
            "schedule_id": item.id, 
            "task_id": item.task.id, 
            "task_name": item.task.task_name, 
            "category_id": item.task.task_category.id, 
            "category_name": item.task.task_category.task_category_name,
            "frequency_or_date": frequency_or_date,
            "memo": item.memo,
        }
        schedules_list.append(schedule)


# 曜日を英語文字列から日本語の曜日に変換するための辞書
weekday_dict = { "MO": "月曜日", "TU": "火曜日", "WE": "水曜日", "TH": "木曜日", "FI": "金曜日", "SA": "土曜日", "SU": "日曜日" }