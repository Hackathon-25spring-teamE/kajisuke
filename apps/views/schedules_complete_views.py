from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date
from ..models import CompletedSchedule



@csrf_exempt
def complete_schedule(request, schedule_id, year, month, day):
    completed_date = date(year, month, day)
    # completed_schedulesから対象条件のレコードを取得
    completed_schedule = CompletedSchedule.objects.filter(
        schedule_id=schedule_id, 
        schedule_date=completed_date,
    )
    