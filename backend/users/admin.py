from django.contrib import admin

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'


admin.site.register(Subscribe)
admin.site.register(User, UserAdmin)
