from django_filters import rest_framework as dfilters
from .models import *

class commentFilter(dfilters.FilterSet):
    class Meta:
        model = blog_comment
        fields = ["blog", "blog__author"]


class blogFilter(dfilters.FilterSet):
    class Meta:
        model = blog
        fields = ["species"]

class blogFilterForManager(dfilters.FilterSet):
    class Meta:
        model = blog
        fields = ["approved", "rejected"]