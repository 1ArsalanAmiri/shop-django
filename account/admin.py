from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.User, UserAdmin)