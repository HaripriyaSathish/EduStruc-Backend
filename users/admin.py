from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display   = ['email', 'full_name', 'role', 'is_active', 'created_at']
    list_filter    = ['role', 'is_active']
    search_fields  = ['email', 'full_name']
    ordering       = ['-created_at']

    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal Info',{'fields': ('full_name', 'phone', 'job_title', 'avatar')}),
        ('Institution',  {'fields': ('institution_name', 'timezone')}),
        ('Role & Access',{'fields': ('role', 'two_fa_enabled')}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'full_name', 'role', 'password1', 'password2',
                        'institution_name', 'phone', 'is_active'),
        }),
    )

    filter_horizontal = ()