from django.contrib import admin
from . import models
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


class LikeAdmin(admin.ModelAdmin):
    pass

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['ref' , 'status' , 'total']
    list_filter = ['status']
    list_select_related = True
    search_fields = ['ref']
    list_editable = ['status']
    list_display_links = ['ref']
    readonly_fields = ['ref' , 'invoice' , 'total' , 'authority' , 'description' , 'user_ip']


admin.site.register(models.Product,ProductAdmin)
admin.site.register(models.Category,CategoryAdmin)
admin.site.register(models.Tag,TagAdmin)
admin.site.register(models.Comment,CommentAdmin)
admin.site.register(models.Like,LikeAdmin)