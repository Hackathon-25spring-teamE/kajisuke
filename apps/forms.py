from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import authenticate

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
    
    #ラベル名をメールアドレスに変更
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "メールアドレス"
    
    #メールアドレスかパスワードが間違っていた場合のエラー
    def clean(self):
        email = self.cleaned_data.get("username")  # フィールド名は username のまま
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError(
                    "メールアドレスもしくはパスワードが間違っています。",
                    code="invalid_login"
                )
            else:
                self.confirm_login_allowed(user)

        return self.cleaned_data