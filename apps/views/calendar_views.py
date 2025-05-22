from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Prefetch
from datetime import datetime, date
from zoneinfo import ZoneInfo
import jpholiday
from dateutil.rrule import rruleset, rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from dateutil.relativedelta import relativedelta
from ..models import PastSchedule, Schedule, ExceptionalSchedule, CompletedSchedule



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
        )

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



# 日付から和暦を算出する
def wareki(date_obj):
    if date_obj.year >= 2019:
        era = "令和"
        year = date_obj.year - 2018
    elif date_obj.year >= 1989:
        era = "平成"
        year = date_obj.year - 1988
    elif date_obj.year >= 1926:
        era = "昭和"
        year = date_obj.year - 1925
    elif date_obj.year >= 1912:
        era = "大正"
        year = date_obj.year - 1911
    elif date_obj.year >= 1868:
        era = "明治"
        year = date_obj.year - 1867
    else:
        return f"{date_obj.year}年"  # 和暦対象外

    year_str = "元" if year == 1 else str(year)
    return f"{era}{year_str}年"


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



# DBクエリで取得したscheduleとexceptional_schedulesから、対象期間（datetime型）の日付リスト（date型）を生成
def get_reccureced_dates(schedule_obj, except_obj, start_date, end_date):
    date_list = []
    # frequencyがNONEの時→schedule_obj.start_dateがstart_dateとend_dateの間であれば日付リストに追加
    if schedule_obj.frequency == "NONE":
        if start_date.date() <= schedule_obj.start_date <= end_date.date():
            date_list.append(schedule_obj.start_date)
    # frequencyがNONE以外の時→繰り返し設定から日付リストを作成する
    else:
        date_set = rruleset()
        reccurences = {
            "freq": frequency_dict.get(schedule_obj.frequency), 
            "interval": schedule_obj.interval, 
            "dtstart": schedule_obj.start_date,
            "bymonth": schedule_obj.start_date.month if schedule_obj.frequency == "YEARLY" else None,
            "byweekday": weekday_dict.get(schedule_obj.day_of_week),
            "bysetpos": schedule_obj.nth_weekday,
        }
        # reccurencesからNoneの項目を除外する
        filted_reccurences = { k: v for k, v in reccurences.items() if v is not None }
        # 上記を使って対象期間の日付リストを作成
        date_set.rrule(
            rrule(**filted_reccurences)
            .between(start_date, end_date, inc=True)
            )

        # 2-3. 日付リストに対し、original_dateを除外し、modified_dateを追加する
        for except_item in except_obj:
            if except_item.schedule.id == schedule_obj.id:
                # 繰り返しからoriginal_dateを除外
                original_date = datetime.combine(except_item.original_date, datetime.min.time())
                date_set.exdate(original_date)
                # modified_dateがNoneではなく、対象期間内なら追加
                if except_item.modified_date is not None:
                    if start_date.date() <= except_item.modified_date <= end_date.date():
                        modified_date = datetime.combine(except_item.modified_date, datetime.min.time())
                        date_set.rdate(modified_date)

        # datetimeをdateに変換
        date_list = [dt.date() for dt in date_set]

    return date_list


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
        6 : { "icon" : "☘", "color" : "#FFC199"},
    }