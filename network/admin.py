from django.contrib import admin
from .models import Post, UserFollow, Like

# Register your models here.
admin.site.register(Post)
admin.site.register(UserFollow)
admin.site.register(Like)