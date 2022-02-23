from django.contrib import admin

# Register your models here.

from .models import User, Post

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ('followers',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'content')
    filter_horizontal = ('likes',)
    readonly_fields = ('timestamp',)

admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
