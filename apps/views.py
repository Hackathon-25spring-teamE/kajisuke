
from django.shortcuts import render ,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View


from .forms import SignupForm, SigninForm

# Create your views here.

# テスト用表示
def hello_world(request):
    context = {
        "message1": "Hello, world.",
        "message2": "KAJISUKEapp is here!",
    }
    # フロントページができたら、以下の形に書き換える（contextは直接渡す）
    # return render(request, '<フロントページのhtml>', context)
    return render(request, 'dev/dev.html', {'context': context})


# サインアップ
class SignupView(CreateView):
    form_class = SignupForm
    template_name = "dev/signup.html"
    success_url = reverse_lazy("apps:hello_world")

    def form_valid(self, form):
        # signin after signup
        response = super().form_valid(form)
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(email=email, password=password)
        
        if user is not None:
            login(self.request, user)
            return response
        else:
            # ログインに失敗した場合、新規登録ページへリダイレクト
            return HttpResponseRedirect(reverse("signup"))

            
# サインイン
class SigninView(BaseLoginView):
    form_class = SigninForm
    template_name = "dev/signin.html"

    def form_valid(self, form):
        # 明示的にログイン
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('apps:hello_world')


# サインアウト
class SignoutView(View):
    def get(self, request):
        logout(request)
        return redirect('apps:signin')
# カレンダー表示

# 日毎のスケジュール表示

# スケジュール登録

# スケジュール変更・削除

# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）