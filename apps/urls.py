from django.urls import path
from .views import hello_world


from . import views

app_name = "apps"

urlpatterns = [
    path('', hello_world, name="hello_world"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('signin/', views.SigninView.as_view(), name="signin"),
    path('signout/', views.SignoutView.as_view(), name="signout")
]