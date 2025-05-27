# フロント開発用mockページ（アプリ完成後は不要）

from django.urls import path
from .views_mock import *

urlpatterns = [
    path('signin/', mock_signin, name="mock_signin"),
    path('signup/', mock_signup, name="mock_signup"),
    path('calendars/year/month/day', mock_calender_day, name="mock_calender_day"),
    path('calendars/year/month', mock_calender_month, name="mock_calender_month"),
    path('schedules/create', mock_add_schedule, name="mock_add_schedule"),
    path('schedules/id/date', mock_edit_oneday, name="mock_edit_oneday"),
    path('schedules/id', mock_edit_schedule, name="mock_edit_schedule"),
    path('schedules/', mock_schedule_list, name="mock_schedule_list"),
    path('', mock_hello_world, name="mock_hello_world"),
    path('myaccount/', mock_myaccount, name="mock_myaccount"),
]