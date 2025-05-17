from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Prefetch
from datetime import datetime, date
from zoneinfo import ZoneInfo
import jpholiday
from dateutil.rrule import rruleset, rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from ..models import PastSchedule, Schedule, ExceptionalSchedule, CompletedSchedule



# カレンダー表示
@login_required
def calendar_month(request, year, month):
    holidays = get_japanese_holidays(year, month)
    print(holidays)
    # 前月を計算
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    # 次月を計算
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    context = {
        "holidays": holidays,
        "current_year": year,
        "current_month": month,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    }
    return render(request, 'calendars/month.html', context)



# 指定された期間のスケジュール一覧をJSONとして返す
@login_required
def schedules_list(request):
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
        )

        # 2-2. 各schedulesで、繰り返し設定からtodayからcalendar_end_dateまでの期間の日付リストを作成する
        for future_item in future_schedules:
            date_list = []
            # frequencyがNONEの時→start_dateが今日以降であれば日付リストに追加
            if future_item.frequency == "NONE":
                if future_item.start_date >= user_today.date():
                    date_list.append(future_item.start_date)
            # frequencyがNONE以外の時→繰り返し設定から日付リストを作成する
            else:
                date_set = rruleset()
                reccurences = {
                    "freq": frequency_dict.get(future_item.frequency), 
                    "interval": future_item.interval, 
                    "dtstart": future_item.start_date,
                    "bymonth": future_item.start_date.month if future_item.frequency == "YEARLY" else None,
                    "byweekday": weekday_dict.get(future_item.day_of_week),
                    "bysetpos": future_item.nth_weekday,
                }
                # reccurencesからNoneの項目を除外する
                filted_reccurences = { k: v for k, v in reccurences.items() if v is not None }
                # 上記を使って対象期間の日付リストを作成
                date_set.rrule(
                    rrule(**filted_reccurences)
                    .between(user_today, calendar_end, inc=True)
                    )

                # 2-3. 日付リストに対し、original_dateを除外し、modified_dateを追加する
                for except_item in exptional_schedules:
                    if except_item.schedule.id == future_item.id:
                        # 繰り返しからoriginal_dateを除外
                        original_date = datetime.combine(except_item.original_date, datetime.min.time())
                        date_set.exdate(original_date)
                        # modified_dateがNoneではなく、対象期間内なら追加
                        if except_item.modified_date is not None:
                            if user_today.date() <= except_item.modified_date <= calendar_end.date():
                                modified_date = datetime.combine(except_item.modified_date, datetime.min.time())
                                date_set.rdate(modified_date)

                # datetimeをdateに変換
                date_list = [dt.date() for dt in date_set]

            # print(item.task.task_name, date_list)

            # 2-4. date_listの各日付にタスク情報を追記して、schedules_listへ追加
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
    view_date = datetime(year, month, day)
    # 今日の日付をdatetimeで取得する
    tz = ZoneInfo("Asia/Tokyo")
    today = timezone.now().astimezone(tz).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)

    schedules_list = []

    # 1.view_date<todayであれば、past_schedulesからview_dateのレコードを取得
    if view_date < today:
        # CompletedScheduleに関するクエリを事前に定義
        completed_schedule_queryset = CompletedSchedule.objects.filter(
            schedule_date=view_date.date()
        )
        # past_schedulesとschedules,tasks,task_categoriesをinner join、
        # さらにcompleted_schedulesをleft joinして、対象ユーザーの対象期間のレコードを取得する
        past_schedules = PastSchedule.objects.filter(
            schedule__user=request.user, 
            schedule_date=view_date.date(),
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
                "memo": past_item.schedule.memo,
                "completed": bool(past_item.schedule.completed_schedules),
            }
            schedules_list.append(schedule)

    # 2.view_date>=todayであれば、schedulesからview_date>=start_dateのレコードを取得
    else:
        # schedulesとtasks,task_categoriesをjoinして、対象ユーザーの対象期間のレコードを取得する
        future_schedules = Schedule.objects.filter(
            user=request.user, 
            is_active=True,
        ).select_related(
            'task__task_category'
        ).order_by('start_date') 

        # 2-1.exptional_schedulesとschedulesをjoinして、
        # 上記条件＋exptional_schedulesの2つのdateのどちらかがview_dateであるレコードを取得
        exptional_schedules = ExceptionalSchedule.objects.filter(
            schedule__user=request.user, 
            schedule__is_active=True,
        ).filter(
        Q(original_date=view_date.date()) | 
        Q(modified_date=view_date.date()) 
        )

        # 2-2.completed_schedulesから対象ユーザーの実施日がview_dateのレコードを取得
        completed_schedules = CompletedSchedule.objects.filter(
            schedule__user=request.user, 
            schedule_date=view_date.date(),
        )

        # 2-3-1.各スケジュール毎に繰り返し設定からview_date期間（1日）のスケジュールを生成
        for future_item in future_schedules:
            date_list = []
            # frequencyがNONEの時→start_dateがview_dateであれば日付リストに追加
            if future_item.frequency == "NONE":
                if future_item.start_date == view_date.date():
                    date_list.append(future_item.start_date)
            # frequencyがNONE以外の時→繰り返し設定から日付リストを作成する
            else:
                date_set = rruleset()
                reccurences = {
                    "freq": frequency_dict.get(future_item.frequency), 
                    "interval": future_item.interval, 
                    "dtstart": future_item.start_date,
                    "bymonth": future_item.start_date.month if future_item.frequency == "YEARLY" else None,
                    "byweekday": weekday_dict.get(future_item.day_of_week),
                    "bysetpos": future_item.nth_weekday,
                }
                # reccurencesからNoneの項目を除外する
                filted_reccurences = { k: v for k, v in reccurences.items() if v is not None }
                # 上記を使って対象期間の日付リストを作成
                date_set.rrule(
                    rrule(**filted_reccurences)
                    .between(view_date, view_date, inc=True)
                    )

                # 2-3-2.各スケジュール毎にexceptional_schedulesの変更を適応
                for except_item in exptional_schedules:
                    if except_item.schedule.id == future_item.id:
                        # 繰り返しからoriginal_dateを除外
                        original_date = datetime.combine(except_item.original_date, datetime.min.time())
                        date_set.exdate(original_date)
                        # modified_dateがNoneではなく、対象期間内なら追加
                        if except_item.modified_date is not None:
                            if view_date.date() <= except_item.modified_date <= view_date.date():
                                modified_date = datetime.combine(except_item.modified_date, datetime.min.time())
                                date_set.rdate(modified_date)

                # datetimeをdateに変換
                date_list = [dt.date() for dt in date_set]

            # 2-3-3.各スケジュール毎にdate_listにスケジュールがあればschedules_listに追加
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
        "view_date": view_date,
        "schedules_list": schedules_list,
    }
    return render(request, 'dev/dev.html', {'context': context})



# 祝日リスト作成
def get_japanese_holidays(year, month):
    holidays = []
    for day in range(1, 32):
        try:
            d = date(year, month, day)
            if jpholiday.is_holiday(d):
                holidays.append(d.strftime('%Y-%m-%d'))
        except ValueError:
            continue
    return holidays


# frequency を文字列からdateutil.rruleの定数に変換するための辞書
frequency_dict = { "DAILY": DAILY, "WEEKLY": WEEKLY, "MONTHLY": MONTHLY, "YEARLY": YEARLY }

# 曜日を文字列からdateutil.rruleの曜日オブジェクトに変換するための辞書
weekday_dict = { "MO": MO,"TU": TU,"WE": WE,"TH": TH,"FI": FR,"SA": SA,"SU": SU }

# 家事カテゴリーのアイコンと色の辞書
category_dict = {
        1 : { "icon" : "🧹", "color" : "#C5D7FB"},
        2 : { "icon" : "🍳", "color" : "#FFE380"},
        3 : { "icon" : "🧺", "color" : "#9BD4B5"},
        4 : { "icon" : "🗂", "color" : "#C0F354"},
        5 : { "icon" : "🌸", "color" : "#99F2FF"},
        6 : { "icon" : "🛠", "color" : "#FFC199"},
    }