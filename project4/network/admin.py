from django.contrib import admin
from .models import User, Post


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    fields = ["content"]


admin.site.register(Post, PostAdmin)
