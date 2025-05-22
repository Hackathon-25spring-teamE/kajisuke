from django.views.generic.edit import CreateView ,UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from datetime import date
from django.utils.timezone import now
from django.urls import reverse


from ..models import Schedule, Task, ExceptionalSchedule
from ..forms import ScheduleForm, ScheduleEditForm, ExceptionalScheduleForm



# スケジュール登録
class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'dev/schedule_create.html'
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
class ScheduleEditAsNewView(UpdateView):
    model = Schedule
    form_class = ScheduleEditForm
    template_name = 'dev/schedule_edit.html'
    success_url = reverse_lazy('apps:hello_world')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        schedule = self.get_object()
        kwargs['user'] = self.request.user
        kwargs['task_category_id'] = schedule.task.task_category_id if schedule.task else None
        return kwargs

    def form_valid(self, form):
        old_schedule = self.get_object()
        old_schedule.is_active = False
        old_schedule.save()

        new_schedule = form.save(commit=False)
        new_schedule.pk = None  # 新規インスタンスとして保存
        new_schedule.user = self.request.user
        new_schedule.task = old_schedule.task  # 編集不可のためフォームから送られてこない
        new_schedule.is_active = True
        new_schedule.save()

        return super().form_valid(form)



# 1日のみの予定変更
class ExceptionalScheduleCreateView(CreateView):
    model = ExceptionalSchedule
    form_class = ExceptionalScheduleForm
    template_name = 'dev/oneday_edit.html'
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
        form.instance.schedule = self.schedule  # 保存前にスケジュールをセット
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule'] = self.schedule
        return context
    



@login_required
def redirect_to_current_calendar(request):
    today = now()
    return redirect('apps:calendar_month', year=today.year, month=today.month)
# スケジュール削除
# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）
