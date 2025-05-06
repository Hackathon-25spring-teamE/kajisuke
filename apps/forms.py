from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 

from .models import CustomUser
from .validators import validate_unique_email, validate_min_length_8, validate_has_digit, validate_has_uppercase



#新規登録用フォーム
class SignUpForm(UserCreationForm):
    user_name = forms.CharField(label="ユーザー名")
    email = forms.EmailField(label="メールアドレス", validators=[validate_unique_email])
    password1 = forms.CharField(label="パスワード", widget=forms.PasswordInput, validators=[validate_min_length_8, validate_has_digit, validate_has_uppercase])
    password2 = forms.CharField(label="パスワード（確認用）", widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ('user_name', 'email', 'password1', 'password2')

    

#ログイン用フォーム
class SigninFrom(AuthenticationForm):
    class Meta:
        model = CustomUser