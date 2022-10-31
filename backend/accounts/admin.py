from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        "last_name"
    )
    search_fields = (
        '^email',
        '^username'
    )
    list_filter = (
        'email',
        'username'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
