from django.views.generic.edit import CreateView ,UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from datetime import date
from django.utils.timezone import now
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.shortcuts import redirect
from zoneinfo import ZoneInfo

from ..models import Schedule, Task, ExceptionalSchedule, CompletedSchedule
from ..forms import ScheduleForm, ScheduleEditForm, ExceptionalScheduleForm
from ..utils.schedule_utils import get_frequency_or_date


# 登録しているスケジュール一覧を表示
@login_required
def schedules_list(request):
    # 今日の日付をdateで取得する
    tz = ZoneInfo("Asia/Tokyo")
    today = now().astimezone(tz).date()

    # schedulesから対象ユーザーのis_active=trueとなっているレコードを全て取得する
    # frequency→intervalで並び替えて取得
    schedules = Schedule.objects.filter(
            user=request.user, 
            is_active=True,
        ).select_related(
            'task__task_category'
        ).annotate(
            frequency_order=Case(
                When(frequency='NONE', then=Value(0)),
                When(frequency='DAILY', then=Value(1)),
                When(frequency='WEEKLY', then=Value(2)),
                When(frequency='MONTHLY', then=Value(3)),
                When(frequency='YEARLY', then=Value(4)),
                default=Value(999),  # 万が一のため
                output_field=IntegerField()
            )
        ).order_by('frequency_order', 'interval')
    
    schedules_list = []

    for item in schedules:
        frequency_or_date = get_frequency_or_date(item, today)
        if frequency_or_date:
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

    context = {     
        "schedules_list": schedules_list,
    }
    return render(request, 'schedules/list.html', context)



# スケジュール登録
class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/create.html'
    success_url = reverse_lazy('apps:hello_world')  # スケジュール一覧などに遷移

    def get_form_kwargs(self):
        """フォームにログインユーザーを渡す"""
        kwargs = super().get_form_kwargs()

        user = self.request.user
        # SimpleLazyObjectなら実インスタンスを取り出す
        if hasattr(user, '_wrapped'):
            user = user._wrapped

        kwargs['user'] = user
        task_category_id = self.request.POST.get('task_category') or self.request.GET.get('task_category')
        kwargs['task_category_id'] = task_category_id
        return kwargs
        
    

    def form_valid(self, form):
        """ログインユーザーをセット"""
        form.instance.user = self.request.user
        return super().form_valid(form)
   


#ユーザーごとの家事とデフォルトの家事のみ表示
@login_required
def load_tasks(request):
    category_id = request.GET.get('task_category')
    user = request.user
    tasks = Task.objects.filter(
        task_category_id=category_id
    ).filter(
        Q(user=None) | Q(user=user)
    )
    return JsonResponse(list(tasks.values('id', 'task_name')), safe=False)



# スケジュール変更
# 繰り返しスケジュール変更
class ScheduleEditAsNewView(LoginRequiredMixin, UpdateView):
    model = Schedule
    form_class = ScheduleEditForm
    template_name = 'dev/schedule_edit.html'
    pk_url_kwarg = 'schedule_id'
    success_url = reverse_lazy('apps:calendar_redirect')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        schedule = self.get_object()
        kwargs['user'] = self.request.user
        kwargs['task_category_id'] = schedule.task.task_category_id if schedule.task else None
        return kwargs

    def form_valid(self, form):
       # 上書き保存するだけ
        schedule = form.save(commit=False)
        schedule.user = self.request.user
        schedule.save()
        return super().form_valid(form)
        


# 1日のみの予定変更・削除
class ExceptionalScheduleCreateView(LoginRequiredMixin, CreateView):
    model = ExceptionalSchedule
    form_class = ExceptionalScheduleForm
    template_name = 'dev/oneday_edit.html'
    pk_url_kwarg = 'schedule_id'
    success_url = reverse_lazy('apps:calendar_redirect')

    def dispatch(self, request, *args, **kwargs):
        self.schedule = get_object_or_404(Schedule, pk=kwargs['schedule_id'])
        self.original_date = date(kwargs['year'], kwargs['month'], kwargs['day'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {
            'original_date': self.original_date
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['schedule'] = self.schedule  # フォームにスケジュールを渡す
        return kwargs

    def form_valid(self, form):
        self.schedule.refresh_from_db()  # 念のため最新状態を取得

        # frequency = 'NONE'（繰り返しなし）の場合は、Scheduleのstart_dateを書き換える
        if self.schedule.frequency == 'NONE':
            modified_date = form.cleaned_data.get('modified_date')
            if modified_date and modified_date != self.schedule.start_date:
                self.schedule.start_date = modified_date
                self.schedule.save(update_fields=["start_date"])
            # 繰り返しでない予定は例外登録不要なのでリダイレクトだけ
            return redirect(reverse('apps:calendar_redirect'))

        # すでに例外が存在する場合は何もしない
        exists = ExceptionalSchedule.objects.filter(
            schedule=self.schedule,
            original_date=self.original_date
        ).exists()
        if exists:
            redirect_url = reverse('apps:calendar_day', kwargs={
                'year': self.original_date.year,
                'month': self.original_date.month,
                'day': self.original_date.day,
            })
            return redirect(f"{redirect_url}?already_modified=true")

        # 通常の繰り返し予定 → 例外スケジュールを作成
        form.instance.schedule = self.schedule
        form.instance.original_date = self.original_date
        response = super().form_valid(form)

        # 登録後に日毎ページに戻る
        redirect_url = reverse('apps:calendar_day', kwargs={
            'year': self.original_date.year,
            'month': self.original_date.month,
            'day': self.original_date.day,
        })
        return redirect(redirect_url)
        
                

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule'] = self.schedule
        # ★ この日付の例外スケジュールがすでに存在しているか確認
        context['is_modified'] = ExceptionalSchedule.objects.filter(
            schedule=self.schedule,
            original_date=self.original_date
        ).exists()

        return context



# 繰り返しスケジュール削除
class ScheduleSoftDeleteView(LoginRequiredMixin, View):
    def post(self, request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, pk=schedule_id)
        schedule.is_active = False
        schedule.save()
        messages.success(request, "スケジュールを削除しました。")
        return redirect(reverse('apps:calendar_redirect'))



# スケジュールの実施・未実施の変更
@login_required
def complete_schedule(request, schedule_id, year, month, day):
    completed_date = date(year, month, day)
    # 対象ユーザーとschedule_idでscheduleを取得→存在しなければエラーを返す
    try:
        schedule = Schedule.objects.get(
            id=schedule_id,
            user=request.user,
        )
    except Schedule.DoesNotExist:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # completed_schedulesから対象条件のレコードを取得
    try:
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
    
    # 上記以外はエラー
    return JsonResponse({'error': 'Invalid request'}, status=400)