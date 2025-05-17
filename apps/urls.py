from django.urls import path
from .views.auth_views import SigninView, SignupView, SignoutView, hello_world

app_name = "apps"

urlpatterns = [
    # テスト用ページ
    path('', hello_world, name="hello_world"),
    # 認証機能
    path('signup', SignupView.as_view(), name="signup"),
    path('signin', SigninView.as_view(), name="signin"),
    path('signout', SignoutView.as_view(), name="signout")
]