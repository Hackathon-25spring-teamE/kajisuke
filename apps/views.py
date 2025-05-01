from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def hello_world(request):
    return HttpResponse("Hello, world. KAJISUKEapp is here!")


# サインアップ

# サインイン

# サインアウト

# カレンダー表示

# 日毎のスケジュール表示

# スケジュール登録

# スケジュール変更・削除

# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）