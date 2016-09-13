"""

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from rest_framework import routers


import videos.views
import videomembership.views
import accounts.views
import comments.views
import notifications.views
import billing.views

from comments.serializers import CommentViewSet
from comments.views import CommentCreateAPIView, CommentDetailAPIView, CommentListAPIView
from videos.serializers import VideoViewSet, CategoryViewSet
from videos.views import CategoryListAPIView, CategoryDetailView, VideoDetailView


router = routers.DefaultRouter()
router.register(r'videos', VideoViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'comment', CommentViewSet)

urlpatterns = [

    url(r'^api2/$', videomembership.views.api_home, name='api_home'),
    url(r'^api2/comment/$', CommentListAPIView.as_view(), name='comment_list_api'),
    url(r'^api2/comment/create/$', CommentCreateAPIView.as_view(), name='comment_create_api'),
    url(r'^api2/comment/(?P<id>\d+)/$', CommentDetailAPIView.as_view(), name='comment_detail_api'),

    url(r'^api2/categories/$', CategoryListAPIView.as_view(), name='category_list_api'),
    url(r'^api2/categories/(?P<slug>[\w-]+)/$', CategoryDetailView.as_view(), name='category_detail_api'),
    url(r'^api2/categories/(?P<cat_slug>[\w-]+)/(?P<vid_slug>[\w-]+)/$', VideoDetailView.as_view(),
        name='video_detail_api'),

    url(r'^api/auth/token/$', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', admin.site.urls),


    url(r'^$', videomembership.views.home, name='home'),
    url(r'^contact/$', TemplateView.as_view(template_name="contact.html"), name='contact'),

    # auth login/logout
    url(r'^login/$', accounts.views.auth_login, name='login'),
    url(r'^logout/$', accounts.views.auth_logout, name='logout'),
    url(r'^register/$', accounts.views.auth_register, name='register'),

    # Become member/billing
    url(r'^upgrade/$', billing.views.upgrade, name='account_upgrade'),
    url(r'^billing/history/$', billing.views.billing_history, name='billing_history'),
    url(r'^billing/cancel/$', billing.views.cancel_subscription, name='cancel_subscription'),

    # Videos
    # mettre les 2 lignes suivantes dans cet ordre sous pein d'avoir 404 à cause de ce qu'il y a après videos/
    url(r'^categories/$', videos.views.category_list, name="category_list"),
    url(r'^categories/(?P<cat_slug>[\w-]+)/$', videos.views.category_detail, name="category_detail"),
    # url(r'^categories/(?P<cat_slug>[\w-]+)/(?P<id_a>\d+)$', videos.views.video_detail, name="video_detail"),
    url(r'^categories/(?P<cat_slug>[\w-]+)/(?P<vid_slug>[\w-]+)$', videos.views.video_detail, name="video_detail"),

    # Comment_thread
    url(r'^comment/(?P<id>\d+)$', comments.views.comment_thread, name='comment_thread'),
    url(r'^comment/create/$', comments.views.comment_create_view, name='comment_create'),

    # notifications
    url(r'^notifications/all/$', notifications.views.all, name='notifications_all'),
    url(r'^notifications/ajax/$', notifications.views.get_notifications_ajax, name='get_notifications_ajax'),
    url(r'^notifications/read/(?P<id>\d+)/$', notifications.views.read, name='notifications_read'),



] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

