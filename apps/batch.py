import logging
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Q
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
from .models import PastSchedule, Schedule, ExceptionalSchedule
from .utils.calendar_utils import get_recurrenced_and_exceptional_dates


# loggerの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 昨日のスケジュールをpast_schedulesテーブルへinsertする
def insert_past_schedules():
    try:
        # 昨日の日付をdatetimeで取得する
        tz = ZoneInfo("Asia/Tokyo")
        today =  timezone.now().astimezone(tz).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0) 
        yesterday = today - relativedelta(days=1)

        logger.info(f'start: insert schedules of {yesterday.date()} to past_schedules')
        
        # 1.is_active=Trueなscheduleを全て取得する
        schedules = Schedule.objects.filter(is_active=True)

        # 2.exptional_schedulesとschedulesをjoinして、
        # 上記条件＋exptional_schedulesの2つのdateのどちらかがyesterdayであるレコードを取得
        exptional_schedules = ExceptionalSchedule.objects.filter(
                schedule__is_active=True,
            ).filter(
            Q(original_date=yesterday.date()) | 
            Q(modified_date=yesterday.date()) 
            ).order_by('id') 
        
        insert_data = []
        
        # 3.各schedule毎に、繰り返し設定からyesterday期間（1日）のスケジュールを生成
        for item in schedules:
            date_list = get_recurrenced_and_exceptional_dates(
                item, 
                exptional_schedules, 
                yesterday, 
                yesterday
            )

            # 4.対象のスケジュールが存在すれば、DBにinsertするデータを追加
            if date_list:
                data = PastSchedule(
                        schedule_id = item.id,
                        schedule_date = yesterday.date(),
                        memo = item.memo,
                        created_at = today,
                        updated_at = today
                )
                insert_data.append(data)

        # 5.insert_dataがあれば、past_schedulesにinsertする
        if insert_data:
            PastSchedule.objects.bulk_create(insert_data, batch_size=1000)
            logger.info(f'[Batch Logic] SUCCESS: schedules of {yesterday.date()}, {len(insert_data)} records inserted')
        else:
            logger.info(f'[Batch Logic] SUCCESS: schedules of {yesterday.date()}, No data to insert')

    # IntegrityError: DB制約に違反する操作を行った場合(一意性制約、NULL制約、外部キー制約など）
    except IntegrityError as e:
        logger.error(f'IntegrityError: {str(e)}')
    # その他のエラーの場合
    except Exception as e:
        logger.error(f'error: {str(e)}')

