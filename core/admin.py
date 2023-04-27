from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from core.models import User


@admin.register(User)
class CustomAdminUser(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',)
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name')})
    )
