import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Create your models here.

#カスタムユーザーを使用するための設定
class CustomUserManager(BaseUserManager):
    def create_user(self, user_name, email, password=None, **extra_fields):
        if not user_name:
            raise ValueError('ユーザー名は必須です')
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(user_name=user_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_name, email, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)   # superuser作成に必要なため追加
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    # 認証に使うフィールドをemailに変更
    USERNAME_FIELD = 'email' 
    # createsuperuserでもuser_nameを必須にする（user_nameがnull不可のため）
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = 'users'



class TaskCategory(models.Model):
    task_category_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_category_name

    class Meta:
        db_table = "task_categories"


class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    task_category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    task_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name

    class Meta:
        db_table = "tasks"


class Schedule(models.Model):
    FREQUENCY_CHOICES = [
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),       
    ]
    DAY_OF_WEEK_CHOICES = [
        ('MO', 'Monday'),
        ('TU', 'Tuseday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FI', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday'),         
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    interval = models.IntegerField(null=True, blank=True)
    day_of_week = models.CharField(max_length=50, choices=DAY_OF_WEEK_CHOICES, null=True, blank=True)
    nth_weekday = models.IntegerField(null=True, blank=True)
    day_of_month = models.IntegerField(null=True, blank=True)
    memo = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task.task_name} ({self.frequency})"

    class Meta:
        db_table = "schedules"


class PastSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    schedule_date = models.DateField()
    memo = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Past: {self.schedule.task.task_name} on {self.schedule_date}"

    class Meta:
        db_table = "past_schedules"
        constraints = [
            models.UniqueConstraint(fields=['schedule', 'schedule_date'], name='unique_schedule_date_past')
        ]


class CompletedSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    schedule_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Completed: {self.schedule.task.task_name} on {self.schedule_date}"

    class Meta:
        db_table = "completed_schedules"
        constraints = [
            models.UniqueConstraint(fields=['schedule', 'schedule_date'], name='unique_schedule_date_complete')
        ]


class ExceptionalSchedule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    original_date = models.DateField()
    modified_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Exception: {self.schedule.task.task_name} on {self.original_date} → {self.modified_date or '削除'}"

    class Meta:
        db_table = "exceptional_schedules"


