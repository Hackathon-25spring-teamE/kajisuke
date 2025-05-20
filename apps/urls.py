from django.urls import path
from .views.auth_views import SigninView, SignupView, SignoutView, hello_world
from .views.calendar_views import calendar_month, calendar_day, schedules_list
from .views.schedules_views import ScheduleCreateView, load_tasks, ScheduleEditAsNewView




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
    path('calendars/<int:year>/<int:month>', calendar_month, name='calendar_month'),
    path('api/schedules', schedules_list, name='schedules_list'),
    #スケジュール登録
    path('schedules/create', ScheduleCreateView.as_view(), name="schedules_create"),
    path('ajax/load-tasks/', load_tasks, name='ajax_load_tasks'),
    # スケジュール繰り返し設定変更
    path('schedule/<int:pk>/edit/', ScheduleEditAsNewView.as_view(), name='schedule_edit'),
]