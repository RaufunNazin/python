from django.contrib import admin
from .models import *

admin.site.register(blog)
admin.site.register(blog_reaction)
admin.site.register(blog_comment)
admin.site.register(blog_stat)

# admin.site.register(blog_reaction_counter)

