__author__ = 'leomaltrait'
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.reverse import reverse
from rest_framework import routers, serializers, permissions, viewsets
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Video, Category
from comments.serializers import CommentSerializer



# works with the VideoDetailView model in views
class VideoUrlHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        kwargs = {
            'cat_slug': obj.category.slug,
            'vid_slug': obj.slug
        }
        return reverse(view_name, kwargs=kwargs, request=request, format=format)




class VideoSerializer(serializers.HyperlinkedModelSerializer):
    url = VideoUrlHyperlinkedIdentityField('video_detail_api')

    category_url = serializers.CharField(source='category.get_absolute_url', read_only=True)
    #category_image = serializers.CharField(source='category.get_image_url', read_only=True)
    #category_title = serializers.CharField(source='category.title', read_only=True)
    # category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    #category = CategorySerializer(many=False, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            'url',
            'id',
            'slug',
            'title',
            'order',
            'embed_code',
            'free_preview',
            'share_message',
            'timestamp',
            # 'category',
            #'category_image',
            #'category_title',
            'category_url',
            'comment_set',
        ]


class VideoViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    queryset = Video.objects.all()
    serializer_class = VideoSerializer



# works with the CategoryDetailView model in views
# class CategoryUrlHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
#      #lookup_field = 'slug'
#
#     def get_url(self, obj, view_name, request, format):
#         kwargs = {
#             'slug': obj.slug
#         }
#         return reverse(view_name, kwargs=kwargs, request=request, format=format)


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    #url = CategoryUrlHyperlinkedIdentityField(view_name='category_detail_api')
    url = serializers.HyperlinkedIdentityField(view_name='category_detail_api', lookup_field='slug')
    video_set = VideoSerializer(many=True)
    class Meta:
        model = Category
        fields = [
            'url',
            'id',
            'title',
            'description',
            'slug',
            'image',
            'video_set'
        ]


class CategoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

