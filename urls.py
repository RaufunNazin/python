from django.urls import path, include
from .api import *

urlpatterns = [
    path('<str:id>/', blogHandler.as_view(), name='Blog'),
    path('approve', approveBlog, name='ApproveBlog'),
    path('reject', rejectBlog, name='RejectBlog'),
    path('likes', blogLikes.as_view(), name='BlogReactions'),
    path('comments', blogComments.as_view(), name='BlogComments'),
    path('like', likeBlog, name='ReactToBlog'),
    path('all', allBlogs.as_view(), name='All Blogs'),
    path('stat', blogStats.as_view(), name='All Blogs'),
    path('', blogsHandler.as_view(), name='Blogs'),
    
]
