from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from zoneinfo import ZoneInfo


# カレンダー表示
def calendar_month(request):
    return render(request, 'calendars/month.html')

# タスク一覧をJSONとして渡す
def task_list(request):
    # ユーザーのTZでの今日の日付を取得する
    user_tz = ZoneInfo(request.GET["timeZone"])
    today = timezone.now().astimezone(user_tz).date()
    # カレンダー表示の開始日と終了日を取得する
    calendar_start_date = datetime.fromisoformat(request.GET["start"]).date()
    calendar_end_date = datetime.fromisoformat(request.GET["end"]).date()
    

    
    print(today)
    print(calendar_start_date)

    # 1. today>calendar_start_dateなら、past_schedulesから対象userのcalendar_start_dateからtoday前までのレコードを取得する
    # past_schedulesとschedules,tasks,task_categoriesをjoin



    # 2. today<=calendar_end_dateなら、schedulesから対象userのis_active=True,start_date<=calendar_end_dateのレコードを取得する
    # 2-1. schedulesの繰り返しから、todayからcalendar_end_dateまでの期間の日付リストを作成する
    # 2-2. exptional_schedulesから対象schedule_idの2つのdateのどちらかがtodayからcalendar_end_dateまでの期間に入っているレコードを取得する
    # 2-3. 日付リストに対し、上記レコードのoriginal_dateを除外（exdate）し、modified_dateを追加（rdate）する
    # 2-4. schedule_id毎に作成した日付リストを、各スケジュール情報を持たせた状態で一つのリストにまとめる
    # 3. 1と2のリストを合わせる
    # 4. completed_schedulesから対象userのcalendar_start_dateからcalendar_end_dateまでのレコードを取得し、3のリストに適応する
    # 5. リストをカレンダー側に渡すデータとしてまとめる
    # 6. データをJSON形式で返す

    # events = Event.objects.all()
    # data = [event.as_dict() for event in events]
    data = [
        {"title":"掃除機", 
         "start":datetime(2025, 5, 1, 10, 0), 
         "end":datetime(2025, 5, 1, 11, 0),
         'className': 'my-events',
        },
        {"title":"洗濯", 
         "start":datetime(2025, 5, 1, 10, 0), 
         "end":datetime(2025, 5, 1, 11, 0),
         'className': 'my-events',
        },
        {"title":"買い物", 
         "start":datetime(2025, 5, 1, 10, 0), 
         "end":datetime(2025, 5, 1, 11, 0),
         'className': 'my-events',
        },
        {"title":"銀行振込", 
         "start":datetime(2025, 5, 1, 10, 0), 
         "end":datetime(2025, 5, 1, 11, 0),
         'className': 'my-events',
        },
        
        ]
    return JsonResponse(data, safe=False)



# 日毎のスケジュール表示
def calendar_day(request, year, month, day):
    context = {
        "message1": "1日のスケジュール一覧",
        "date": f'{year}年 {month}月 {day}日',
    }
    return render(request, 'dev/dev.html', {'context': context})

