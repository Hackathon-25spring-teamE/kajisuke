from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.rrule import rruleset, rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from ..models import PastSchedule, Schedule, ExceptionalSchedule


# カレンダー表示
@login_required
def calendar_month(request):
    return render(request, 'calendars/month.html')

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
            schedule_date__gte=calendar_start.date()
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
            start_date__lte=calendar_end.date(),
            is_active=True
        ).select_related(
            'task__task_category'
        ).order_by('start_date') 

        # 2-1. exptional_schedulesとschedulesをjoinして、
        # 上記条件＋exptional_schedulesの2つのdateのどちらかがtodayからcalendar_end_dateまでの期間に入っているレコードを取得する
        exptional_schedules = ExceptionalSchedule.objects.filter(
            schedule__user=request.user, 
            schedule__start_date__lte=calendar_end.date(),
            schedule__is_active=True,
        ).filter(
        Q(original_date__gte=user_today.date(), original_date__lte=calendar_end.date()) |  # original_dateが期間内
        Q(modified_date__gte=user_today.date(), modified_date__lte=calendar_end.date())    # modified_dateが期間内
        )

        # frequency を文字列からdateutil.rruleの定数に変換するための辞書
        frequency_dict = { "DAILY": DAILY, "WEEKLY": WEEKLY, "MONTHLY": MONTHLY, "YEARLY": YEARLY }
        # 曜日を文字列からdateutil.rruleの曜日オブジェクトに変換するための辞書
        weekday_dict = { "MO": MO,"TU": TU,"WE": WE,"TH": TH,"FR": FR,"SA": SA,"SU": SU }


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
                
                print(future_item.task.task_name, list(date_set))


                # 2-3. 日付リストに対し、original_dateを除外し、modified_dateを追加する
                for except_item in exptional_schedules:
                    if except_item.schedule.id == future_item.id:
                        # 繰り返しからoriginal_dateを除外
                        original_date = datetime.combine(except_item.original_date, datetime.min.time())
                        date_set.exdate(original_date)
                        # modified_dateがNoneでなければ追加
                        if except_item.modified_date is not None:
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
    context = {
        "message1": "1日のスケジュール一覧",
        "date": f'{year}年 {month}月 {day}日',
    }
    return render(request, 'dev/dev.html', {'context': context})


category_dict = {
        1 : { "icon" : "🧹", "color" : "#C5D7FB"},
        2 : { "icon" : "🍳", "color" : "#FFE380"},
        3 : { "icon" : "🧺", "color" : "#9BD4B5"},
        4 : { "icon" : "🗂", "color" : "#C0F354"},
        5 : { "icon" : "🌸", "color" : "#99F2FF"},
        6 : { "icon" : "🛠", "color" : "#FFC199"},
    }