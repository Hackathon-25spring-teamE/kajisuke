from django.shortcuts import render ,redirect
from django.contrib.auth import login, logout, authenticate
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView

from django.utils import timezone


from ..forms import SignupForm, SigninForm


# Create your views here.

# サインアップ
class SignupView(CreateView):
    form_class = SignupForm
    template_name = "signup.html"
    success_url = reverse_lazy("apps:calendar_redirect")

    def dispatch(self, request, *args, **kwargs):
        # すでにログインしていたらカレンダーにリダイレクト
        if request.user.is_authenticated:
            return redirect('apps:calendar_redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # サインアップに成功したら、サインインする
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
    template_name = "signin.html"
    redirect_authenticated_user = True
    

    def form_valid(self, form):
        # 明示的にログイン
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('apps:calendar_redirect')


# サインアウト
class SignoutView(View):
    def get(self, request):
        logout(request)
        return redirect('apps:signin')
