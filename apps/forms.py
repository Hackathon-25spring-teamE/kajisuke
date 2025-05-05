from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 



#新規登録用フォーム


#ログイン用フォーム
class EmailSigninForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス', max_length=254)