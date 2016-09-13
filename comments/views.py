from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, HttpResponseRedirect, get_object_or_404

from rest_framework import generics, permissions, mixins, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from notifications.signals import notify
from videos.models import Video

from .forms import CommentForm
from .models import Comment
from .permissions import IsOwnerOrReadOnly
from .serializers import CreateCommentSerializer, CommentSerializer, UpdateCommentSerializer



class CommentListAPIView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    paginate_by = 2


class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CreateCommentSerializer


class CommentDetailAPIView(mixins.DestroyModelMixin, mixins.UpdateModelMixin, generics.RetrieveAPIView):
    # queryset = Comment.objects.all()  # doestn't get children comment
    serializer_class = UpdateCommentSerializer
    permission_classes = [IsOwnerOrReadOnly, ]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        queryset = Comment.objects.filter(pk__gte=0) # primary key greater than or equal to 0 (so everything)
        return queryset


@login_required
def comment_thread(request, id):
    comment = get_object_or_404(Comment, id=id)
    form = CommentForm()
    context = {
        "form": form,
        "comment": comment,
    }
    return render(request, 'comments/comment_thread.html', context)

def comment_create_view(request):
    if request.method == "POST" and request.user.is_authenticated():
        parent_id = request.POST.get('parent_id')
        video_id = request.POST.get('video_id')
        origin_path = request.POST.get("origin_path")

        try:
            video = Video.objects.get(id=video_id)
        except:
            video = None

        parent_comment = None
        if parent_id is not None:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
            except:
                parent_comment = None
                #TODO

            if parent_comment is not None and parent_comment.video is not None:
                video = parent_comment.video
        form = CommentForm(request.POST)

        if form.is_valid():
            comment_text = form.cleaned_data['comment'] # 'comment' is th name of the attr in comments/forms.py


            if parent_comment is not None:
                new_comment = Comment.objects.create_comment(
                    user=request.user,
                    path=parent_comment.get_origin,
                    text=comment_text,
                    video=video,
                    parent=parent_comment
                )
                affected_users = parent_comment.get_affected_users()
                notify.send(
                    request.user,
                    action=new_comment,
                    target=parent_comment,
                    recipient=parent_comment.user,
                    affected_users=affected_users,
                    verb="replied to"
                )
                messages.success(request, 'Thank you for your response.', extra_tags=['alert-success'])
                return HttpResponseRedirect(parent_comment.get_absolute_url())
            else:
                new_comment = Comment.objects.create_comment(
                    text=comment_text,
                    user=request.user,
                    path=origin_path,
                    video=video
                )
                # Eventually change to  send a notif to superuser/staff to answer any comment on the website
                # notify.send(
                #     request.user,
                #     recipient=request.user,
                #     action=new_comment,
                #     target=new_comment.video,
                #     verb="commented on"
                # )
                messages.success(request, 'Thank you for your comment.', extra_tags=['alert-success'])
                return HttpResponseRedirect(new_comment.get_absolute_url())
        #TODO ce elif est un else different dans le tuto
        elif form.errors and parent_comment is None:
            messages.error(request, 'There were an error with your comment.', extra_tags=['alert-danger'])
            return HttpResponseRedirect(origin_path)

        #TODO ce else n'exist pas dans le tuto
        else:
            messages.error(request, 'There were an error with your comment.', extra_tags=['alert-danger'])
            return HttpResponseRedirect(parent_comment.get_absolute_url())
    else:
        raise Http404




























