from django.urls import path
from .views.auth_views import SigninView, SignupView, SignoutView, hello_world

app_name = "apps"
from apps.views.calendar_views import calendar_month, calendar_day, task_list

urlpatterns = [
    path('calendars/<int:year>/<int:month>/<int:day>', calendar_day, name='calendar_day'),
    path('calendars/', calendar_month, name='calendar_view'),
    path('api/tasks/', task_list, name='task_list'),
    # path('', views.hello_world, name="hello_world"),
    path('signup', views.SignupView.as_view(), name="signup"),
    path('signin', views.SigninView.as_view(), name="signin"),
    path('signout', views.SignoutView.as_view(), name="signout")
]