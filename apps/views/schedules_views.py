from django.views.generic.edit import CreateView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from ..models import Schedule, Task
from ..forms import ScheduleForm



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

# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）
