# portfolio/admin.py
from django.contrib import admin
from .models import *

# Register your models here.

# Custom admin for BlogPost
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'author')
    list_filter = ('published_at', 'author')
    search_fields = ('title', 'content')
    # Automatically creates the slug from the title
    prepopulated_fields = {'slug': ('title',)} 

admin.site.register(About)
admin.site.register(Skill)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Project)
admin.site.register(SocialLink)
admin.site.register(BlogPost, BlogPostAdmin) 