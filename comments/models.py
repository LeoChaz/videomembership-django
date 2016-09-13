from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect

from accounts.models import MyUser
from videos.models import Video


class CommentManager(models.Manager):

    def all(self):
        return super(CommentManager, self).filter(active=True).filter(parent=None)

    def recent(self):
        return self.get_queryset().filter(active=True).filter(parent=None)[:5]

    def create_comment(self, text=None, user=None, path=None, video=None, parent=None):
        if not path:
            raise ValueError('Must have a path when adding a comment')
        if not path:
            raise ValueError('Must be logged in when adding a comment')

        comment = self.model(
            text = text,
            user = user,
            path = path
        )
        if video is not None:
            comment.video = video
        if parent is not None:
            comment.parent= parent
        comment.save(using=self._db)
        return comment


# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(MyUser)
    parent = models.ForeignKey('self', null=True, blank=True) # commentaire de commentaire
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    active = models.BooleanField(default=True)

    path = models.CharField(max_length=350)
    video = models.ForeignKey(Video, null=True, blank=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        #return "{} - {}".format(self.text, self.user.username)
        return self.user.username

    def get_absolute_url(self):
        return reverse('comment_thread', kwargs={"id": self.id})

    @property
    def get_origin(self):
        return self.path

    @property   # permet d'appeler la fonction avec comment.get_comment au lieu de comment.get_comment()
    def get_comment(self):
        return self.text

    @property
    def is_child(self):
        if self.parent is not None:
            return True
        else:
            return False

    def get_children(self):
        if self.is_child:
            return None
        else:
            return Comment.objects.filter(parent=self)

    def get_affected_users(self):
        """
        It needs to be a parent and have children;
        the children, in effect, are the affected users.
        """
        comment_children = self.get_children()
        if comment_children is not None:
            users = []
            for comment in comment_children:
                if comment.user in users:
                    pass
                else:
                    users.append(comment.user)
            return users
        return None



