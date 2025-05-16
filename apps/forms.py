from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import authenticate
from django.db.models import Q


from .models import CustomUser, Schedule, Task, TaskCategory
from .validators import validate_unique_email, validate_min_length_8, validate_has_digit, validate_has_uppercase



#サインアップ用フォーム
class SignupForm(UserCreationForm):
    user_name = forms.CharField(label="ユーザー名")
    email = forms.EmailField(label="メールアドレス", validators=[validate_unique_email])
    password1 = forms.CharField(label="パスワード", widget=forms.PasswordInput, validators=[validate_min_length_8, validate_has_digit, validate_has_uppercase])
    password2 = forms.CharField(label="パスワード（確認用）", widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ('user_name', 'email', 'password1', 'password2')



#サインイン用フォーム
class SigninForm(AuthenticationForm):
    
    #ラベル名をメールアドレスに変更
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].label = "メールアドレス"
    
    #メールアドレスかパスワードが間違っていた場合のエラー
    def clean(self):
        email = self.cleaned_data.get("username")  # フィールド名は username のまま
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                print("認証に失敗しました")
                raise forms.ValidationError(
                    "メールアドレスもしくはパスワードが間違っています。",
                    code="invalid_login"
                )
            else:
                self.confirm_login_allowed(user)
                self.user_cache = user

        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)


# スケジュール新規登録用のフォーム
FREQUENCY_CHOICES = [
    ('NONE', 'なし'),
    ('DAILY', '毎日'),
    ('WEEKLY', '毎週'),
    ('MONTHLY', '毎月'),
    ('YEARLY', '毎年'),
]

class ScheduleForm(forms.ModelForm):
    task_category = forms.ModelChoiceField(
        queryset=TaskCategory.objects.all(),
        required=True,
        label="カテゴリー"
    )
    task = forms.ModelChoiceField(
        queryset=Task.objects.none(),  # 初期状態は空
        required=True,
        label="家事"
    )
    frequency = forms.ChoiceField(
        choices=FREQUENCY_CHOICES,
        label="繰り返し設定",
        widget=forms.HiddenInput()  # 見た目には表示しない（ボタンに置き換えるため）
    )
    

    class Meta:
        model = Schedule
        fields = ['start_date', 'task_category', 'task', 'memo', 'frequency', 'interval', 'day_of_week', 'nth_weekday', 'day_of_month']
        labels = {
        'task': '家事',
        'start_date': '開始日',
        'frequency': '繰り返し設定',
        'interval': '間隔（週ごと、月ごと）',
        'day_of_week': '曜日',
        'nth_weekday': '第何曜日',
        'day_of_month': '月の何日',
        'memo': 'メモ',
    }

    def __init__(self, *args, user=None, task_category_id=None, **kwargs):
        # userが文字列ならCustomUserを取得
        if isinstance(user, str):
            try:
                user = CustomUser.objects.get(user_name=user)
            except CustomUser.DoesNotExist:
                user = None
        #デバック用
        print("userの型・ID・ユーザー名:", type(user), getattr(user, 'pk', None), getattr(user, 'user_name', None))

        self.user = user
        print("ユーザー:", user)#テスト用後で消す
        super().__init__(*args, **kwargs)

        #カスタムウェジェット
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})

        # task_category_id は引数から受け取る
        if task_category_id is None:
            # POSTやGETから fallback で取る
            task_category_id = self.data.get('task_category') or task_category_id

        # task_category_id を整数に変換
        try:
            task_category_id = int(task_category_id)
        except (TypeError, ValueError):
            task_category_id = None

        # 🔽 ここに追加してください！
        print("フォーム初期化: user =", user)
        print("フォーム初期化: task_category_id =", task_category_id)


        if user:
            self.fields['task_category'].queryset = TaskCategory.objects.all()

            if task_category_id:
                tasks = Task.objects.filter(
                    Q(task_category_id=task_category_id),
                    Q(user=None) | Q(user=user),
                    is_active=True,
                )
                print("該当するタスク:", tasks)
                self.fields['task'].queryset = tasks
            else:
                self.fields['task'].queryset = Task.objects.none()
        else:
            self.fields['task'].queryset = Task.objects.none()