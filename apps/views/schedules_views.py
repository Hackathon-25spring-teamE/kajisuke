from django.views.generic.edit import CreateView ,UpdateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import Schedule, Task
from ..forms import ScheduleForm, ScheduleEditForm



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

# スケジュール変更・削除
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
# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）
