from django.urls import path
from .views import hello_world, CustomSigninView

from . import views

urlpatterns = [
    path('', hello_world, name="hello_world"),
    path('signin/', views.CustomSigninView.as_view(), name='Signin'),
]