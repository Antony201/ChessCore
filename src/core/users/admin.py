from .forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django.contrib.auth import admin as auth_admin, get_user_model
from .models import Role

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (('User', {'fields': ('id', 'avatar', 'city', 'description', 'role')}),)+auth_admin.UserAdmin.fieldsets
    list_display = ["username", 'email', "is_superuser", 'role', 'is_active']
    search_fields = ["first_name"]
    readonly_fields = ['id']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass
