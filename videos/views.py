from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import render, Http404, HttpResponseRedirect, get_object_or_404

from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from analytics.signals import page_view
#from comments.models import Comment
from comments.forms import Comment, CommentForm
from comments.models import CommentManager

from .models import Video, Category, TaggedItem
from .permissions import IsMember
from .serializers import CategorySerializer, VideoSerializer


class VideoDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsMember]

    def get_object(self):
        vid_slug = self.kwargs['vid_slug']
        cat_slug = self.kwargs['cat_slug']
        cat = get_object_or_404(Category, slug=cat_slug)
        obj = get_object_or_404(Video, category=cat, slug=vid_slug)
        return obj


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 10

    # def get_queryset(self):
        # user = self.request.user
        # return user.accounts.all()


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        slug = self.kwargs['slug']
        obj = get_object_or_404(Category, slug=slug)
        return obj




#@login_required
def video_detail(request, cat_slug, vid_slug):  # id -> cf urls.py
    cat = get_object_or_404(Category, slug=cat_slug)
    obj = get_object_or_404(Video, slug=vid_slug, category=cat)
    page_view.send(
        request.user,
        page_path=request.get_full_path(),
        primary_obj=obj,
        secondary_obj=cat
    )
    if request.user.is_authenticated() or obj.has_preview:
        try:
            is_member = request.user.is_member
        except:
            is_member = None
        if is_member or obj.has_preview:
            comments = obj.comment_set.all()
            for c in comments:
                c.get_children()
            comment_form = CommentForm()
            return render(request, 'videos/video_detail.html', {"obj":obj, "comments":comments, "comment_form":comment_form})
        else:
            # TODO upgrade account
            next_url = obj.get_absolute_url()
            return HttpResponseRedirect('{}?next={}'.format(reverse('account_upgrade'), next_url))
    else:
        next_url = obj.get_absolute_url()
        return HttpResponseRedirect('{}?next={}'.format(reverse('login'), next_url))



def category_list(request):
    queryset = Category.objects.all()
    context = {
        'queryset': queryset,
    }
    return render(request, 'videos/category_list.html', context)


#@login_required
def category_detail(request, cat_slug):
    cat = get_object_or_404(Category, slug=cat_slug)
    videos = cat.video_set.all()
    page_view.send(
        request.user,
        page_path=request.get_full_path(),
        primary_obj=cat
    )
    return render(request, 'videos/video_list.html', {"cat": cat, "videos": videos})




# def video_edit(request):
#     render(request, 'videos/video_edit.html', {})
#
# def video_create(request):
#     render(request, 'videos/video_create.html', {})

















