from django.shortcuts import render

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

# サインアウト

# カレンダー表示

# 日毎のスケジュール表示

# スケジュール登録

# スケジュール変更・削除

# スケジュール実施・未実施

# 登録しているスケジュール表示

# 昨日のスケジュールをpast_schedulesへ登録（バッチ処理）