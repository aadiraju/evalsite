
from django.contrib import admin

# Register your models here.
from .models import Video, UserVideoJunction

admin.site.register(Video)
admin.site.register(UserVideoJunction)
