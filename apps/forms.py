from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now

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
JAPANESE_DAY_OF_WEEK_CHOICES = [
    ('MO', '月曜日'),
    ('TU', '火曜日'),
    ('WE', '水曜日'),
    ('TH', '木曜日'),
    ('FI', '金曜日'),
    ('SA', '土曜日'),
    ('SU', '日曜日'),
]

class ScheduleForm(forms.ModelForm):
    task_category = forms.ModelChoiceField(queryset=TaskCategory.objects.all(),required=True,label="カテゴリー")
    task = forms.ModelChoiceField(queryset=Task.objects.none(), required=True,label="家事") # 初期状態は空
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES,label="繰り返し設定",widget=forms.HiddenInput() ) # 見た目には表示しない（ボタンに置き換えるため）
    day_of_week = forms.ChoiceField(choices=JAPANESE_DAY_OF_WEEK_CHOICES, required=False)

    class Meta:
        model = Schedule
        fields = ['start_date', 'task_category', 'task', 'memo', 'frequency', 'interval', 'day_of_week', 'nth_weekday']
        labels = {
        'task': '家事',
        'start_date': '開始日',
        'frequency': '繰り返し設定',
        'interval': '間隔',
        'day_of_week': '曜日',
        'nth_weekday': '第何曜日',
        'memo': 'メモ',
    }
        widgets = {
            'memo': forms.Textarea(attrs={
                'placeholder': 'メモ',
                'rows': 3  # 高さの調整（任意）
            }),
        }

    #開始日を今日以降に制限する
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError("開始日は今日以降の日付を選択してください。")
        return start_date
    
    # YEARLY × by_date のとき、day_of_weekとnth_weekdayクリア
    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get("frequency")

        # yearly_option は hidden ではなくJS制御の外部フィールドなので、self.data から取得
        if frequency == "YEARLY":
            yearly_option = self.data.get("yearly_option")  # POSTデータから取得（formフィールドには含まれていない想定）

            if yearly_option == "by_date":
                # by_date選択時は曜日系フィールドを空に
                cleaned_data["day_of_week"] = None
                cleaned_data["nth_weekday"] = None

        # MONTHLY: by_date のとき曜日情報をクリア
        if frequency == "MONTHLY":
            monthly_option = self.data.get("monthly_option")
            if monthly_option == "by_date":
                cleaned_data["day_of_week"] = None
                cleaned_data["nth_weekday"] = None

        return cleaned_data

    def __init__(self, *args, user=None, task_category_id=None, **kwargs):
        # userが文字列ならCustomUserを取得
        if isinstance(user, str):
            try:
                user = CustomUser.objects.get(user_name=user)
            except CustomUser.DoesNotExist:
                user = None
        self.user = user
        super().__init__(*args, **kwargs)

        # frequencyが「なし」以外のときは interval の初期値を1に
        frequency = self.data.get('frequency') or self.initial.get('frequency')
        if frequency and frequency != 'NONE':  # ← 'none' はFREQUENCY_CHOICESの値に合わせてください
            self.fields['interval'].initial = 1

        #  当日の日付を初期値に設定（ただし既に指定されていないときだけ上書きしないように）
        if not self.initial.get('start_date') and not self.data.get('start_date'):
            self.initial['start_date'] = now().date()

        #カスタムウェジェット
        #今日より前の日付は選べないように制限
        today_str = timezone.now().date().strftime('%Y-%m-%d')
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date', 'min': today_str})

        # task_category_id は引数から受け取る
        if task_category_id is None:
            # POSTやGETから fallback で取る
            task_category_id = self.data.get('task_category') or task_category_id

        # task_category_id を整数に変換
        try:
            task_category_id = int(task_category_id)
        except (TypeError, ValueError):
            task_category_id = None


        if user:
            self.fields['task_category'].queryset = TaskCategory.objects.all()
            self.fields['task_category'].empty_label = 'カテゴリ'

            if task_category_id:
                tasks = Task.objects.filter(
                    Q(task_category_id=task_category_id),
                    Q(user=None) | Q(user=user),
                    is_active=True,
                )
                self.fields['task'].queryset = tasks
                self.fields['task'].empty_label = '家事'
            else:
                self.fields['task'].queryset = Task.objects.none()
                self.fields['task'].empty_label = '家事'
        else:
            self.fields['task'].queryset = Task.objects.none()
            self.fields['task'].empty_label = '家事'