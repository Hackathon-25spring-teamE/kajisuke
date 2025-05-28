from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now
from django.utils.dateparse import parse_date

from .models import CustomUser, Schedule, Task, TaskCategory, ExceptionalSchedule
from .validators import validate_unique_email, validate_min_length_8, validate_has_digit, validate_has_uppercase



#サインアップ用フォーム
class SignupForm(UserCreationForm):
    user_name = forms.CharField(label="ユーザー名", widget=forms.TextInput(attrs={'placeholder': 'name'}))
    email = forms.EmailField(label="メールアドレス", validators=[validate_unique_email],widget=forms.EmailInput(attrs={'placeholder': 'E-mail'}))
    password1 = forms.CharField(label="パスワード",  validators=[validate_min_length_8, validate_has_digit, validate_has_uppercase],widget=forms.PasswordInput(attrs={'placeholder': 'Password'}) )
    password2 = forms.CharField(label="パスワード（確認用）", widget=forms.PasswordInput(attrs={'placeholder': 'Password(confirm)'}))
    
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

        # プレースホルダーを追加
        self.fields['username'].widget.attrs.update({
            'placeholder': 'E-mail'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password'
        })
    
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
    task_category = forms.ModelChoiceField(queryset=TaskCategory.objects.all(),required=True,label="--カテゴリー--")
    task = forms.ModelChoiceField(queryset=Task.objects.none(), required=True,label="--家事--") # 初期状態は空
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES,label="繰り返し設定",widget=forms.HiddenInput() ) # 見た目には表示しない（ボタンに置き換えるため）
    day_of_week = forms.ChoiceField(choices=JAPANESE_DAY_OF_WEEK_CHOICES, required=False)
    nth_weekday = forms.IntegerField(required=False, widget=forms.HiddenInput())
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
                'placeholder': '--メモ--',
                'rows': 3  # 高さの調整（任意）
            }),
        }

    #開始日を今日以降に制限する
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < timezone.now().date():
            raise forms.ValidationError("開始日は今日以降の日付を選択してください。")
        return start_date
    
    def clean_interval(self):
        interval = self.cleaned_data.get('interval')
        frequency = self.cleaned_data.get('frequency')

        # frequency が NONE 以外のとき、interval が空なら 1 を補完
        if frequency != 'NONE' and not interval:
            return 1
        return interval
    
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
    

    def save(self, commit=True):
        instance = super().save(commit=False)

        # by_dateの場合にnth_weekdayを明示的にクリア
        frequency = self.cleaned_data.get("frequency")
        monthly_option = self.data.get("monthly_option")
        yearly_option = self.data.get("yearly_option")

        if (frequency == "MONTHLY" and monthly_option == "by_date") or \
        (frequency == "YEARLY" and yearly_option == "by_date"):
            instance.nth_weekday = None

        # WEEKLY の場合は nth_weekday をクリア
        if frequency == "WEEKLY":
            instance.nth_weekday = None

        # DAILY または NONE の場合は day_of_week と nth_weekday をクリア
        if frequency in ["DAILY", "NONE"]:
            instance.day_of_week = None
            instance.nth_weekday = None

        if commit:
            instance.save()
        return instance
    



    def __init__(self, *args, user=None, task_category_id=None, request=None, **kwargs):
        self.request = request
        # userが文字列ならCustomUserを取得
        if isinstance(user, str):
            try:
                user = CustomUser.objects.get(user_name=user)
            except CustomUser.DoesNotExist:
                user = None
        self.user = user
        super().__init__(*args, **kwargs)

        #  開始日: リンクからの ?date= を使う処理 ---
        today = now().date()
        if not self.data.get('start_date'):  # POSTによるユーザー入力がなければ
            date_str = request.GET.get('date') if request else None
            parsed_date = parse_date(date_str) if date_str else None
            if parsed_date and parsed_date >= today:
                self.initial.setdefault('start_date', parsed_date)
            else:
                self.initial.setdefault('start_date', today)

        # 繰り返し頻度が設定されているが間隔が未指定の場合は初期値1をセット 
        if not self.data:
            frequency = self.initial.get('frequency') or (self.instance and self.instance.frequency)
            interval = self.initial.get('interval') or (self.instance and self.instance.interval)
            if frequency and frequency != 'NONE' and interval is None:
                self.fields['interval'].initial = 1

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

        # ユーザー独自の家事とデフォルトをフィルタリング
        if user:
            self.fields['task_category'].queryset = TaskCategory.objects.all()
            self.fields['task_category'].empty_label = '--カテゴリー--'

            if task_category_id:
                tasks = Task.objects.filter(
                    Q(task_category_id=task_category_id),
                    Q(user=None) | Q(user=user),
                    is_active=True,
                )
                self.fields['task'].queryset = tasks
                self.fields['task'].empty_label = '--家事--'
            else:
                self.fields['task'].queryset = Task.objects.none()
                self.fields['task'].empty_label = '--家事--'
        else:
            self.fields['task'].queryset = Task.objects.none()
            self.fields['task'].empty_label = '--家事--'



# スケジュール繰り返し設定編集用のフォーム
class ScheduleEditForm(ScheduleForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 既存データがあれば編集モードとみなす
        if self.instance.pk:
            self.fields['task_category'].disabled = True
            self.fields['task'].disabled = True

            self.fields['task_category'].initial = self.instance.task.task_category
            self.fields['task'].initial = self.instance.task

            # 表示用のラベル
            self.task_category_label = str(self.instance.task.task_category)
            self.task_label = str(self.instance.task)

        # start_date に初期値がなければ instance.start_date を使う
        if not self.fields['start_date'].initial:
            self.fields['start_date'].initial = self.instance.start_date



        # start_date に初期値がなければ instance.start_date を使う
        if not self.fields['start_date'].initial:
            self.fields['start_date'].initial = self.instance.start_date
            self.fields['day_of_week'].initial = self.instance.day_of_week
            self.fields['nth_weekday'].initial = self.instance.nth_weekday
            self.fields['frequency'].initial = self.instance.frequency
            self.fields['interval'].initial = self.instance.interval
            self.fields['memo'].initial = self.instance.memo
            self.fields['start_date'].initial = self.instance.start_date

        # intervalフィールドのinputにCSSクラスを追加
        self.fields['interval'].widget.attrs.update({'class': 'interval'})





# 1日のみの予定を編集用のフォーム
class ExceptionalScheduleForm(forms.ModelForm):
    class Meta:
        model = ExceptionalSchedule
        fields = ['original_date', 'modified_date']
        labels = {
            'original_date': '予定日',
            'modified_date': '変更日',
        }
        widgets = {
            'original_date': forms.DateInput(attrs={'type': 'date'}),
            'modified_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    #変更日を今日以降に制限する
    def clean_modified_date(self):
        modified_date = self.cleaned_data.get('modified_date')
        if modified_date and modified_date < timezone.now().date():
            raise forms.ValidationError("開始日は今日以降の日付を選択してください。")
        return modified_date
    
    def __init__(self, *args, **kwargs):
        schedule = kwargs.pop('schedule', None)
        super().__init__(*args, **kwargs)
        # original_date は表示専用
        self.fields['original_date'].disabled = True

        if schedule:
            self.instance.schedule = schedule  # 関連付け

        #  当日の日付を初期値に設定（ただし既に指定されていないときだけ上書きしないように）
        if not self.initial.get('modified_date') and not self.data.get('modified_date'):
            self.initial['modified_date'] = now().date()

        #カスタムウェジェット
        #今日より前の日付は選べないように制限
        today_str = timezone.now().date().strftime('%Y-%m-%d')
        self.fields['modified_date'].widget = forms.DateInput(attrs={'type': 'date', 'min': today_str})