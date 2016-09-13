#from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render, HttpResponseRedirect, redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response as RestResponse
from rest_framework.reverse import reverse as api_reverse

from accounts.forms import RegisterForm, LoginForm
from accounts.models import MyUser
from analytics.models import PageView
from analytics.signals import page_view
from comments.models import Comment
from videos.models import Video, Category


@api_view(["GET"])
def api_home(request):
    data = {
        "categories": {
            "url": api_reverse("category_list_api"),
            "count": Category.objects.all().count(),
        },
        "comments": {
            "url": api_reverse("comment_list_api"),
            "count": Comment.objects.all().count(),
        },
    }
    return RestResponse(data)

#@login_required(login_url="/login/")
#@login_required
def home(request):
    page_view.send(
        request.user,
        page_path=request.get_full_path()
    )
    if request.user.is_authenticated():
        page_view_objs = request.user.pageview_set.get_videos()[:4] # les 3 videos les plus récentes
        recent_videos = []
        for obj in page_view_objs:
            if not obj.primary_object in recent_videos:
                recent_videos.append(obj.primary_object)

        recent_comments = Comment.objects.recent()

        # 3 Most viewed videos
        video_type = ContentType.objects.get_for_model(Video)
        popular_videos_list = PageView.objects.filter(primary_content_type=video_type).values("primary_object_id").annotate(the_count=Count("primary_object_id")).order_by("-the_count")[:3]
        popular_videos = []
        for vid in popular_videos_list:
            video = Video.objects.get(id=vid["primary_object_id"])
            popular_videos.append(video)

        # One video id=10
        #PageView.objects.filter(primary_content_type=video_type, primary_object_id=10).count()

        context = {
            "recent_videos": recent_videos,
            "recent_comments": recent_comments,
            "popular_videos": popular_videos
        }
        template = 'home_logged_in.html'
    else:
        featured_categories = Category.objects.get_featured()
        featured_videos = Video.objects.get_featured()
        register_form = RegisterForm()
        login_form = LoginForm()
        context = {
            "register_form": register_form,
            "login_form": login_form,
            "featured_videos": featured_videos,
            "featured_categories": featured_categories
        }
        template = 'home_visitor.html'
    return render(request, template, context)


# A UTILISER SI ON VEUT MONTRER DIFFÉRENTES HOMEPAGE AUX USERS EN FONCTION DE LOGUÉ OU PAS
# def home(request):
#     if request.user.is_authenticated():
#         name = "Léo"
#         videos = Video.objects.all()
#         embeds = []
#         for video in videos:
#             embeds.append("{}".format(video.embed_code))
#
#         context = {
#             "the_name": name,
#             "number": videos.count(),
#             "videos": videos,
#             "embeds": embeds,
#         }
#         return render(request, 'home_logged_in.html', context)
#     #redirect to login
#     else:
#         return HttpResponseRedirect('/login/')


@login_required(login_url="/staff/login")
def staff_home(request):

    context = {

    }
    return render(request, 'home_logged_in.html', context)



