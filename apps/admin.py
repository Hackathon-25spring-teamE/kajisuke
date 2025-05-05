from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TaskCategory, Task, Schedule, PastSchedule, CompletedSchedule, ExceptionalSchedule

# Register your models here.

admin.site.register(TaskCategory)
admin.site.register(Task)
admin.site.register(Schedule)
admin.site.register(PastSchedule)
admin.site.register(CompletedSchedule)
admin.site.register(ExceptionalSchedule)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'user_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('email', 'user_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'user_name', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'password1', 'password2', 'is_staff')}
        ),
    )
