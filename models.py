from django.db import models
import uuid
from petprofile.models import species

from django.contrib.auth import get_user_model
User = get_user_model()

def upload_to(instance, filename):
    return 'images/{filename}{str(uuid.uuid4())}'.format(filename=filename)

class blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=1023)
    body = models.TextField()
    coverImg = models.ImageField(upload_to="blog/", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)

    species = models.ForeignKey(species, on_delete=models.SET_NULL, null=True, blank=True)

    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

class blog_reaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(blog, on_delete=models.CASCADE)
    reactor = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.reactor.name + " likes " + self.blog.title

class blog_comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(blog, on_delete=models.CASCADE)
    reactor = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.reactor.name + " commented on " + self.blog.title

class blog_stat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(blog, on_delete=models.CASCADE)
    hits = models.BigIntegerField(default=0)
    likes = models.BigIntegerField(default=0)
    comments = models.BigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.blog.title} | {str(self.hits)} hits - {str(self.likes)} likes - {str(self.comments)} comments"