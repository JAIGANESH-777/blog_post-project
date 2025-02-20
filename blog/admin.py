from django.contrib import admin
from .models import Post,Category,about_user
# Register your models here.
class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'content')
    list_filter = ('category', 'created_at')
admin.site.register(Post,PostAdmin) 
admin.site.register(Category)
admin.site.register(about_user)
