from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

from users.serializers import shortUserSerializer

class BlogSerializer(serializers.ModelSerializer):
    author = shortUserSerializer()
    class Meta:
        model = blog
        fields = ['id', 'title', 'coverImg', 'body', 'author', 'created', 'modified']

        def to_representation(self, instance):
            self.fields['author'] = shortUserSerializer
            return super(shortUserSerializer, self).to_representation(instance)

class shortBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog
        fields = ['id', 'title']

class blogSerializerForManager(serializers.ModelSerializer):
    class Meta:
        model = blog
        fields = ['id', 'title', 'approved', 'rejected', 'created']


class writeBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog
        fields = ('title', 'body', 'coverImg',)
        def to_representation(self, instance):
            return super(self).to_representation(instance)

class ReactionSerializer(serializers.ModelSerializer):
    reactor = shortUserSerializer()
    class Meta:
        model = blog_reaction
        fields = ['reactor']

class commentSerializer(serializers.ModelSerializer):
    reactor = shortUserSerializer()
    blog = shortBlogSerializer()
    class Meta:
        model = blog_comment
        fields = ['id', 'comment', 'blog', 'reactor', 'created']
        def to_representation(self, instance):
            return super(self).to_representation(instance)

class writeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog_comment
        fields = ['blog', 'comment']
        def to_representation(self, instance):
            return super(self).to_representation(instance)


class blogStatSerializer(serializers.ModelSerializer):
    blog = shortBlogSerializer()
    class Meta:
        model = blog_stat
        fields = '__all__'

