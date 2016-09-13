from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.urlresolvers import reverse
from django.db import models



from .signals import notify



class NotificationQuerySet(models.query.QuerySet):
    def get_user(self, recipient):
        return self.filter(recipient=recipient)

    def mark_targetless(self, recipient):
        qs = self.unread().get_user(recipient)
        qs_no_target = qs.filter(target_object_id=None)
        if qs_no_target:
            qs_no_target.update(read=True)

    def mark_all_read(self, recipient):
        qs = self.unread().get_user(recipient)
        qs.update(read=True)

    def mark_all_unread(self, recipient):
        qs = self.read().get_user(recipient)
        qs.update(read=False)

    def read(self):
        return self.filter(read=True)

    def unread(self):
        return self.filter(read=False)

    def recent(self):
        return self.unread()[:5]


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def all_unread(self, user):
        return self.get_queryset().get_user(user).unread()

    def all_read(self, user):
        return self.get_queryset().get_user(user).read()

    def all_for_user(self, user):
        self.get_queryset().mark_targetless(user)
        return self.get_queryset().get_user(user)




class Notification(models.Model):
    sender_content_type = models.ForeignKey(ContentType, related_name="notify_sender")
    sender_object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey('sender_content_type', 'sender_object_id')

    verb = models.CharField(max_length=255) #a verb related to what's going on

    action_content_type = models.ForeignKey(ContentType, related_name="notify_action", null=True, blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey('action_content_type', 'action_object_id')

    target_content_type = models.ForeignKey(ContentType, related_name="notify_target", null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey('target_content_type', 'target_object_id')


    #sender = models.ForeignKey()

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications')

    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    read = models.BooleanField(default=False)
    objects = NotificationManager()

    def __str__(self):
        try:
            target_url = self.target_object.get_absolute_url()
        except:
            target_url = None
        context = {
            "sender": self.sender_object,
            "verb": self.verb,
            "target": self.target_object,
            "action": self.action_object,
            "verified_read": reverse('notifications_read', kwargs={"id": self.id}),
            "target_url": target_url,

        }
        if self.target_object:
            if self.action_object and target_url:
               return "{sender} {verb} <a href='{verified_read}?next={target_url}'>{target}</a> with {action}.".format(**context)
            if self.action_object and not target_url:
                return '{sender} {verb} {target} with {action}.'.format(**context)
            return "{sender} {verb} {target}.".format(**context)
        return "{sender} {verb}.".format(**context)

    @property
    def get_link(self):
        try:
            target_url = self.target_object.get_absolute_url()
        except:
            target_url = reverse('notifications_all')

        context = {
            "sender": self.sender_object,
            "verb": self.verb,
            "target": self.target_object,
            "action": self.action_object,
            "target_url": target_url,
            "verified_read": reverse("notifications_read", kwargs={"id": self.id})
        }
        if self.target_object:
            return "<a href='{verified_read}?next={target_url}'>{sender} {verb} {target} with {action}.</a>".format(**context)
        else:
            return "<a href='{verified_read}?next={target_url}'>{sender} {verb}.</a>".format(**context)


def new_notification(sender, **kwargs):
    #new_notification_create = Notification.objects.create(recipient=recipient, action=action)
    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    verb = kwargs.pop('verb')
    affected_users = kwargs.pop('affected_users', None)
    #print(affected_users)
    #print(sender)
    # target = kwargs.pop('target', None)
    # action = kwargs.pop('action', None)

    if affected_users is not None:
        for each_user in affected_users:
            if each_user == sender:
                pass
            else:
                print(each_user)
                new_note = Notification(
                    recipient=each_user,
                    verb=verb,
                    sender_content_type = ContentType.objects.get_for_model(sender),
                    sender_object_id = sender.id
                )

                for option in ("target", "action"):
                    #obj = kwargs.pop(option, None) #not working here because with pop the value associated to option
                    #  will disappear after one lap through the for loop
                    try:
                        obj = kwargs[option] # try block in case of None
                        if obj is not None:
                            setattr(new_note, "{}_content_type".format(option), ContentType.objects.get_for_model(obj))
                            setattr(new_note, "{}_object_id".format(option), obj.id)
                    except:
                        pass

                # if target is not None:
                #     new_note.target_content_type = ContentType.objects.get_for_model(target)
                #     new_note.target_object_id = target.id
                # if action is not None:
                #     new_note.action_content_type = ContentType.objects.get_for_model(action)
                #     new_note.action_object_id = action.id
                new_note.save()
                #print(new_note)

    else:
        new_note = Notification(
            recipient=recipient,
            verb=verb,
            sender_content_type = ContentType.objects.get_for_model(sender),
            sender_object_id = sender.id
        )

        for option in ("target", "action"):
            obj = kwargs.pop(option, None)
            if obj is not None:
                setattr(new_note, "{}_content_type".format(option), ContentType.objects.get_for_model(obj))
                setattr(new_note, "{}_object_id".format(option), obj.id)

        new_note.save()
        #print(new_note)


notify.connect(new_notification)












