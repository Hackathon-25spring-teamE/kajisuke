from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 

from .models import User


#新規登録用フォーム


#ログイン用フォーム
class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス', max_length=254)