# フロント開発用mockページ（アプリ完成後は不要）

from django.shortcuts import render


# テスト用表示
def mock_hello_world(request):
    return render(request, 'dev/hello_world.html')


# サインアップ
def mock_signup(request):
    return render(request, 'signup.html')

# サインイン
def mock_signin(request):
    return render(request, 'signin.html')

# カレンダー表示
def mock_calender_month(request):
    return render(request, 'calendars/month.html')

# 日毎のスケジュール表示
def mock_calender_day(request):
    return render(request, 'calendars/day.html')

# スケジュール登録
def mock_add_schedule(request):
    return render(request, 'schedules/create.html')

# スケジュール設定変更・削除
def mock_edit_schedule(request):
    return render(request, 'schedules/edit_schedules.html')

# 1日のみの変更・削除
def mock_edit_oneday(request):
    return render(request, 'schedules/edit_oneday.html')

# 登録しているスケジュール表示
def mock_schedule_list(request):
    return render(request, 'schedules/list.html')
