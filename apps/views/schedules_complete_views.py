from django.http import JsonResponse
from datetime import date
from ..models import CompletedSchedule


# スケジュールの実施・未実施の変更
def complete_schedule(request, schedule_id, year, month, day):
    completed_date = date(year, month, day)
    try:
        # completed_schedulesから対象条件のレコードを取得
        completed_record = CompletedSchedule.objects.get(
            schedule_id=schedule_id, 
            schedule_date=completed_date,
        )
    except CompletedSchedule.DoesNotExist:
        completed_record = None

    # POSTであれば、completed_schedulesにレコードを追加
    if request.method == 'POST':
        if completed_record is None:
            try:
                completed_schedule = CompletedSchedule(
                    schedule_id=schedule_id,
                    schedule_date=completed_date, 
                )
                completed_schedule.save()
            except:
                return JsonResponse({'error': 'failed to complete'}, status=400)
        
        return JsonResponse({'status': 'completed'}, status=200)
    
    # DELETEであれば、completed_schedulesのレコードを削除          
    elif request.method == 'DELETE':
        if completed_record:
            completed_record.delete()
        return JsonResponse({'status': 'not_completed'}, status=200)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
        