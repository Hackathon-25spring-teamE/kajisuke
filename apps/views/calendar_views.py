from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Prefetch
from datetime import datetime, date
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
from ..models import PastSchedule, Schedule, ExceptionalSchedule, CompletedSchedule
from ..utils.calendar_utils import get_reccureced_dates, get_japanese_holidays, wareki



# カレンダー表示
@login_required
def calendar_month(request, year, month):
    # 表示する月の初日のdateを作成
    current_month_date = date(year, month, 1)
    # 和暦を算出
    wareki_year = wareki(current_month_date)
    # 表示する月の祝日を取得
    holidays = get_japanese_holidays(year, month)

    context = {
        "current_month": current_month_date,
        "wareki_year": wareki_year,
        "prev_month": current_month_date - relativedelta(months=1),
        "next_month": current_month_date + relativedelta(months=1),
        "holidays": holidays,
    }
    return render(request, 'calendars/month.html', context)



# 指定された期間のスケジュール一覧をJSONとして返す
@login_required
def schedules_of_month(request):
    # ユーザーのTZでのtodayをdatetimeで取得する
    user_tz = ZoneInfo(request.GET["timeZone"])
    user_today = timezone.now().astimezone(user_tz).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    # カレンダー表示の開始日と終了日をdatetimeで取得する
    calendar_start = datetime.fromisoformat(request.GET["start"])
    calendar_end = datetime.fromisoformat(request.GET["end"])
    
    schedules_list = []

    # 1. user_now>calendar_start_dateなら、past_schedulesから対象userのcalendar_start_dateからtoday前までのレコードを取得する
    if user_today.date() > calendar_start.date():
        # past_schedulesとschedules,tasks,task_categoriesをjoinして、対象ユーザーの対象期間のレコードを取得する
        past_schedules = PastSchedule.objects.filter(
            schedule__user=request.user, 
            schedule_date__gte=calendar_start.date(),
            schedule_date__lte=calendar_end.date(),
        ).select_related(
            'schedule__task__task_category'
        ).order_by('schedule_date') 

        # schedules_listにタスク情報を追記してスケジュールに追加
        for past_item in past_schedules:
            category_settings = category_dict.get(past_item.schedule.task.task_category.id)
            schedule = {
                "title": category_settings["icon"] + past_item.schedule.task.task_name, 
                "start": past_item.schedule_date, 
                "end": past_item.schedule_date,
                "allDay": True,
                'textColor': "#333333",
                'backgroundColor': category_settings["color"], 
            }
            schedules_list.append(schedule)


    # 2. user_now<=calendar_end_dateなら、schedulesから対象userのis_active=True,start_date<=calendar_end_dateのレコードを取得する
    if user_today.date() <= calendar_end.date():
        # schedulesとtasks,task_categoriesをjoinして、対象ユーザーの対象期間のレコードを取得する
        future_schedules = Schedule.objects.filter(
            user=request.user, 
            is_active=True
        ).select_related(
            'task__task_category'
        ).order_by('start_date') 

        # 2-1. exptional_schedulesとschedulesをjoinして、
        # 上記条件＋exptional_schedulesの2つのdateのどちらかがtodayからcalendar_end_dateまでの期間に入っているレコードを取得する
        exptional_schedules = ExceptionalSchedule.objects.filter(
            schedule__user=request.user, 
            schedule__is_active=True,
        ).filter(
        Q(original_date__gte=user_today.date(), original_date__lte=calendar_end.date()) |  # original_dateが期間内
        Q(modified_date__gte=user_today.date(), modified_date__lte=calendar_end.date())    # modified_dateが期間内
        ).order_by('id') 

        # 2-2. 各schedulesで、繰り返し設定からtodayからcalendar_end_dateまでの期間の日付リストを作成する
        for future_item in future_schedules:
            date_list = get_reccureced_dates(
                future_item, 
                exptional_schedules, 
                user_today, 
                calendar_end
            )
            # 2-3. date_listの各日付にタスク情報を追記して、schedules_listへ追加
            for dt in date_list:
                category_settings = category_dict.get(future_item.task.task_category.id)
                schedule = {
                    "title": category_settings["icon"] + future_item.task.task_name, 
                    "start": dt, 
                    "end": dt,
                    "allDay": True,
                    'textColor': "#333333",
                    'backgroundColor': category_settings["color"], 
                }
                schedules_list.append(schedule)    
                
    # 3. schedules_listをJSON形式で返す
    return JsonResponse(schedules_list, safe=False)



# 日毎のスケジュール表示
@login_required
def calendar_day(request, year, month, day):
    # 表示する日付をdatetimeで取得する
    current_date = datetime(year, month, day)
    # 今日の日付をdatetimeで取得する
    tz = ZoneInfo("Asia/Tokyo")
    today = timezone.now().astimezone(tz).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    
    is_editable = True
    schedules_list = []

    # 1.current_date<todayであれば、past_schedulesからcurrent_dateのレコードを取得
    if current_date < today:
        # past_schedulesのレコードは変更不可
        is_editable = False
        # CompletedScheduleに関するクエリを事前に定義
        completed_schedule_queryset = CompletedSchedule.objects.filter(
            schedule_date=current_date.date()
        )
        # past_schedulesとschedules,tasks,task_categoriesをinner join、
        # さらにcompleted_schedulesをleft joinして、対象ユーザーの対象期間のレコードを取得する
        past_schedules = PastSchedule.objects.filter(
            schedule__user=request.user, 
            schedule_date=current_date.date(),
        ).select_related(
            'schedule__task__task_category'
        ).prefetch_related(
            Prefetch(
                'schedule__completedschedule_set', 
                queryset=completed_schedule_queryset, 
                to_attr='completed_schedules'
                )
        )

        # print(past_schedules[0].schedule.completed_schedules)

        # schedules_listにタスク情報を追記してスケジュールに追加
        for past_item in past_schedules:
            schedule = {
                "schedule_id": past_item.schedule.id, 
                "task_id": past_item.schedule.task.id, 
                "task_name": past_item.schedule.task.task_name, 
                "category_id": past_item.schedule.task.task_category.id, 
                "category_name": past_item.schedule.task.task_category.task_category_name,
                "memo": past_item.memo,
                "completed": bool(past_item.schedule.completed_schedules),
            }
            schedules_list.append(schedule)

    # 2.view_date>=todayであれば、schedulesから対象のレコードを取得
    else:
        # schedulesとtasks,task_categoriesをjoinして、対象ユーザーの対象期間のレコードを取得する
        future_schedules = Schedule.objects.filter(
            user=request.user, 
            is_active=True,
        ).select_related(
            'task__task_category'
        ).order_by('start_date') 

        # 2-1.exptional_schedulesとschedulesをjoinして、
        # 上記条件＋exptional_schedulesの2つのdateのどちらかがcurrent_dateであるレコードを取得
        exptional_schedules = ExceptionalSchedule.objects.filter(
            schedule__user=request.user, 
            schedule__is_active=True,
        ).filter(
        Q(original_date=current_date.date()) | 
        Q(modified_date=current_date.date()) 
        ).order_by('id') 

        # 2-2.completed_schedulesから対象ユーザーの実施日がcurrent_dateのレコードを取得
        completed_schedules = CompletedSchedule.objects.filter(
            schedule__user=request.user, 
            schedule_date=current_date.date(),
        )

        # 2-3-1.各スケジュール毎に繰り返し設定からcurrent_date期間（1日）のスケジュールを生成
        for future_item in future_schedules:
            date_list = get_reccureced_dates(
                future_item, 
                exptional_schedules, 
                current_date, 
                current_date
            )
            # 2-3-2.各スケジュール毎にdate_listにスケジュールがあればschedules_listに追加
            if date_list:
                # completed_schedulesに各スケジュールIDがあれば、実施済みにする
                completed = False
                for comp_item in completed_schedules:
                    if future_item.id == comp_item.schedule.id:
                        completed = True
                        break

                schedule = {
                    "schedule_id": future_item.id, 
                    "task_id": future_item.task.id, 
                    "task_name": future_item.task.task_name, 
                    "category_id": future_item.task.task_category.id, 
                    "category_name": future_item.task.task_category.task_category_name,
                    "memo": future_item.memo,
                    "completed": completed,
                }
                schedules_list.append(schedule)

    context = {
        "current_date": current_date,
        "prev_date": current_date - relativedelta(days=1),
        "next_date": current_date + relativedelta(days=1),
        "is_editable": is_editable,     
        "schedules_list": schedules_list,
    }
    return render(request, 'calendars/day.html', context)



# 今月のカレンダーにリダイレクトする
@login_required
def redirect_to_current_calendar(request):
    today = timezone.now()
    return redirect('apps:calendar_month', year=today.year, month=today.month)



# 家事カテゴリーのアイコンと色の辞書
category_dict = {
        1 : { "icon" : "🧹", "color" : "#C5D7FB"},
        2 : { "icon" : "🍳", "color" : "#FFE380"},
        3 : { "icon" : "🧺", "color" : "#9BD4B5"},
        4 : { "icon" : "🗂", "color" : "#C0F354"},
        5 : { "icon" : "🌸", "color" : "#99F2FF"},
        6 : { "icon" : "☘", "color" : "#FFC199"},
    }