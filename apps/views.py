
from django.shortcuts import render ,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# Create your views here.

# テスト用表示
def hello_world(request):
    context = {
        "message1": "Hello, world.",
        "message2": "KAJISUKEapp is here!",
    }
    # フロントページができたら、以下の形に書き換える（contextは直接渡す）
    # return render(request, '<フロントページのhtml>', context)
    return render(request, 'dev/dev.html', {'context': context})


# サインアップ

# サインイン
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = EmailLoginForm
# サインアウト

# カレンダー表示

# 日毎のスケジュール表示

# スケジュール登録

# スケジュール変更・削除

# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）