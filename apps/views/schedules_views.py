from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from ..models import Schedule, Task
from ..forms import ScheduleForm



# スケジュール登録
class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedule/schedule_form.html'
    success_url = reverse_lazy('schedule_list')  # スケジュール一覧などに遷移

    def get_form_kwargs(self):
        """フォームにログインユーザーを渡す"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """ログインユーザーをセット"""
        form.instance.user = self.request.user
        return super().form_valid(form)
    
def load_tasks(request):
    category_id = request.GET.get('task_category')
    user = request.user
    tasks = Task.objects.filter(task_category_id=category_id).filter(user__in=[None, user])
    return JsonResponse(list(tasks.values('id', 'task_name')), safe=False)

#カテゴリーにひもづくタスクの取得
@login_required
def get_tasks_by_category(request):
    category_id = request.GET.get('category_id')
    tasks = Task.objects.filter(task_category_id=category_id).filter(user__in=[None, request.user])
    task_list = [{'id': task.id, 'name': task.task_name} for task in tasks]
    return JsonResponse({'tasks': task_list})
# スケジュール変更・削除

# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）
