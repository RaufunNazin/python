from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, filters, status
from django_filters import rest_framework as dfilters
from rest_framework.response import Response
from .serializers import *
from .filters import *
from .models import blog
from django.contrib.auth import get_user_model
User = get_user_model()

def statUpdate(blogId, mode):

    if blog.objects.filter(id=blogId).exists():
        selectedBlog = blog.objects.get(id=blogId)
        blogStat, createdBlogStat = blog_stat.objects.get_or_create(blog=selectedBlog)
        if mode == "hit":
            blogStat.hits = blogStat.hits + 1
        if mode == "reaction":
            blogStat.likes = blogStat.likes + 1
        if mode == "unreaction":
            blogStat.likes = blogStat.likes - 1
        if mode == "comment":
            blogStat.comments = blogStat.comments + 1

        blogStat.save()

class blogsHandler(generics.ListCreateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = BlogSerializer
            return serializer_class
        elif self.request.method == 'POST':
            serializer_class = writeBlogSerializer
            return serializer_class
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)
    
    filter_backends = [dfilters.DjangoFilterBackend]
    filterset_class = blogFilter

    def get_queryset(self):
        return blog.objects.filter(approved=True).filter(deleted=False).filter(rejected=False).order_by('created')

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        # Check if user is writer
        if user.groups.filter(name='Writer').exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            try:
                serializedCoverImg = serializer.validated_data['coverImg']
                newBlog = blog(title=serializer.validated_data['title'],body=serializer.validated_data['body'],author=user,coverImg=serializedCoverImg)
            except:
                newBlog = blog(title=serializer.validated_data['title'],body=serializer.validated_data['body'],author=user)

            newBlog.save()
            return Response({'success' : "true"},status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Not Enough Permission'
            }, status=401)

class blogHandler(generics.RetrieveUpdateAPIView):
    
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = BlogSerializer
            return serializer_class
        elif self.request.method == 'PATCH':
            serializer_class = writeBlogSerializer
            return serializer_class

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'PATCH':
            return (permissions.IsAuthenticated(),)

    def get_queryset(self):
        return blog.objects.filter(approved=True).filter(deleted=False).filter(rejected=False)
    
    def get(self, request, *args, **kwargs):
        blogId = self.request.path[9:-1]
        statUpdate(blogId, "hit") # * Update Blog
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        # Check if user is write
        user = User.objects.get(id=request.user.id)
        if user.groups.filter(name='Writer').exists():
            if self.get_object().author == user:
                serializer = self.get_serializer(self.get_object(), data=request.data, partial=kwargs['partial'])
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response({
                    'success': False,
                    'error': 'User not Owner'
                }, status=401)
        else:
            return Response({
                'success': False,
                'error': 'Not Enough Permission'
            }, status=401)

class allBlogs(generics.ListAPIView):
    serializer_class = blogSerializerForManager
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [dfilters.DjangoFilterBackend]
    filterset_class = blogFilterForManager

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        userIsWriterManager = user.groups.filter(name='WriterManager').exists()
        userIsWriter = user.groups.filter(name='Writer').exists()
        if user.is_superuser or userIsWriterManager:
            return blog.objects.filter(deleted=False).order_by('created')
        elif userIsWriter:
            return blog.objects.filter(deleted=False).filter(author=user).order_by('created')
        else:
            return blog.objects.none()

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def approveBlog(request):
    # Must provide blog
    try:
        blogId = request.GET["blog"]
    except:
        return Response({'success': False, 'error': 'Blog not provided'}, status=403)

    # blog id must be valid
    if blog.objects.filter(id=blogId).exists() == False:
        return Response({'success': False,'error': 'Enter valid blog'}, status=403)
    selectedBlog = blog.objects.get(id=blogId)

    # user must be in WriterManager group
    user = User.objects.get(id=request.user.id)
    if user.groups.filter(name='WriterManager').exists() == False:
        return Response({'success': False,'error': 'Only Writer Manager Can Approve'}, status=403)

    # blog mustn't be already approved
    if selectedBlog.approved:
        return Response({'success': False,'error': 'Blog already approved'}, status=403)

    # approve blog
    selectedBlog.approved = True
    selectedBlog.rejected = False
    selectedBlog.save()
    return Response({'success': True,}, status=200)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def rejectBlog(request):
    # Must provide blog
    try:
        blogId = request.GET["blog"]
    except:
        return Response({'success': False, 'error': 'Blog not provided'}, status=403)

    # blog id must be valid
    if blog.objects.filter(id=blogId).exists() == False:
        return Response({'success': False,'error': 'Enter valid blog'}, status=403)
    selectedBlog = blog.objects.get(id=blogId)

    # user must be in WriterManager group
    user = User.objects.get(id=request.user.id)
    if user.groups.filter(name='WriterManager').exists() == False:
        return Response({'success': False,'error': 'Only Writer Manager Can Approve'}, status=403)

    # approve blog
    selectedBlog.approved = False
    selectedBlog.rejected = True
    selectedBlog.save()
    return Response({'success': True,}, status=200)

class blogLikes(generics.ListAPIView):
    serializer_class = ReactionSerializer
    permission_classes = [permissions.AllowAny]
    queryset = blog_reaction.objects.all()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def likeBlog(request):
    try:
        blogId = request.GET["blog"]
    except:
        return Response({'success': False, 'error': 'blog is no provided'}, status=403)
    
    # * blog id must be valid
    if blog.objects.filter(id=blogId).exists() == False:
        return Response({'success': False,'error': 'Enter valid blog'}, status=403)
    selectedBlog = blog.objects.get(id=blogId)

    user = User.objects.get(id=request.user.id)
    if blog_reaction.objects.filter(blog=selectedBlog).filter(reactor=user).exists():
        # * Delete Blog Reaction
        blog_reaction.objects.filter(blog=selectedBlog).filter(reactor=user).delete()
        statUpdate(blogId, "unreaction") # * Update Blog
        return Response({'success': True}, status=200)

    # * Create new blog reaction
    blogReaction = blog_reaction(blog=selectedBlog, reactor=user)
    blogReaction.save()
    statUpdate(blogId, "reaction") # * Update Blog
    return Response({'success': True}, status=200)

class blogComments(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            serializer_class = commentSerializer
            return serializer_class
        elif self.request.method == 'POST':
            serializer_class = writeCommentSerializer
            return serializer_class

    filter_backends = [dfilters.DjangoFilterBackend]
    filterset_class = commentFilter

    def get_permissions(self):
        if self.request.method == 'GET':
            return (permissions.AllowAny(),)
        elif self.request.method == 'POST':
            return (permissions.IsAuthenticated(),)

    queryset = blog_comment.objects.all()

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if blog.objects.filter(id=serializer.data['blog']).exists() == False:
            return Response({'success': False, 'error': 'blog is not valid'}, status=403)

        newComment = blog_comment(blog= blog.objects.get(id=serializer.data['blog']),reactor=user,comment=serializer.data['comment'])
        newComment.save()
        statUpdate(serializer.data['blog'], "comment") # * Update Blog
        return Response({
            'comment': commentSerializer(newComment, context=self.get_serializer_context()).data,
        })

class blogStats(generics.ListAPIView):
    serializer_class = blogStatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        userIsWriterManager = user.groups.filter(name='WriterManager').exists()
        userIsWriter = user.groups.filter(name='Writer').exists()

        if user.is_superuser or userIsWriterManager:
            return blog_stat.objects.all()
        elif userIsWriter:
            return blog_stat.objects.filter(blog__author=user)
        else:
            return blog.objects.none()