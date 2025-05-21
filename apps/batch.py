from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .models import PastSchedule, Schedule, ExceptionalSchedule
from .views.calendar_views import get_reccureced_dates




def insert_past_schedules():
    print('APSchedulerのテストです')

    # 昨日の日付をdatetimeで取得する
    tz = ZoneInfo("Asia/Tokyo")
    yesterday =  timezone.now().astimezone(tz).replace(tzinfo=None).replace(
        hour=0, minute=0, second=0, microsecond=0) - relativedelta(days=1)
    
    # 1.is_active=Trueなscheduleを全て取得する
    schedules = Schedule.objects.filter(is_active=True)

    # 2.exptional_schedulesとschedulesをjoinして、
    # 上記条件＋exptional_schedulesの2つのdateのどちらかがyesterdayであるレコードを取得
    exptional_schedules = ExceptionalSchedule.objects.filter(
            schedule__is_active=True,
        ).filter(
        Q(original_date=yesterday.date()) | 
        Q(modified_date=yesterday.date()) 
        )
    
    # 3.各schedule毎に、繰り返し設定からyesterday期間（1日）のスケジュールを生成
    for item in schedules:
        date_list = get_reccureced_dates(
            item, 
            exptional_schedules, 
            yesterday, 
            yesterday
        )

    # 4.対象のスケジュールがあれば、DBにinsertするデータを準備
    # 5.past_schedulesにinsertする


def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(insert_past_schedules, 'cron', hour=0, minute=1)
    scheduler.add_job(insert_past_schedules, 'cron', hour=0, minute=37)
    scheduler.start()