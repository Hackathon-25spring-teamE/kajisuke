from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


# メールの重複チェック
def validate_unique_email(value):
    if CustomUser.objects.filter(email=value).exists():
        raise ValidationError(_('このメールアドレスはすでに使用されています。'))


# パスワードの追加チェック
def validate_min_length_8(value):
    if len(value) < 8:
        raise ValidationError("パスワードは8文字以上である必要があります。")

def validate_has_digit(value):
    if not any(c.isdigit() for c in value):
        raise ValidationError("パスワードには少なくとも1つの数字が必要です。")

def validate_has_uppercase(value):
    if not any(c.isupper() for c in value):
        raise ValidationError("パスワードには少なくとも1つの大文字が必要です。")
    
    