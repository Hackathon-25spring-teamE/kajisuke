from django.urls import path
from .views.auth_views import SigninView, SignupView, SignoutView, hello_world
from .views.calendar_views import calendar_month, calendar_day, task_list


app_name = "apps"

urlpatterns = [
    # テスト用ページ
    path('', hello_world, name="hello_world"),
    # 認証機能
    path('signup', SignupView.as_view(), name="signup"),
    path('signin', SigninView.as_view(), name="signin"),
    path('signout', SignoutView.as_view(), name="signout"),
    # カレンダー表示
    path('calendars/<int:year>/<int:month>/<int:day>', calendar_day, name='calendar_day'),
    path('calendars/', calendar_month, name='calendar_month'),
    path('api/tasks/', task_list, name='task_list'),
]