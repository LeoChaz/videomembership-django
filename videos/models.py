from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.utils.http import urlquote
from django.utils.text import slugify


from .utils import get_vid_for_direction



class VideoQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)

    def has_embed(self):
        return self.exclude(embed_code__exact="")
        #return self.filter(embed_code__isnull=False).exclude(embed_code__exact="")


class VideoManager(models.Manager):
    def get_queryset(self):
        return VideoQuerySet(self.model, using=self._db)

    def get_featured(self):
        # Video.objects.filter(featured=True)
        #return super(VideoManager, self).filter(featured=True)
        return self.get_queryset().active().featured()

    def all(self):
        return self.get_queryset().active().has_embed().order_by('order')

DEFAULT_MESSAGE = """
Check out this video!
"""

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=120)
    embed_code = models.CharField(max_length=500, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    share_message = models.TextField(default=DEFAULT_MESSAGE)
    order = models.PositiveIntegerField(default=1)
    tags = GenericRelation("TaggedItem", null=True, blank=True)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    free_preview = models.BooleanField(default=False)

    # on n'aurait pas besoins de quotes si la class Category se trouvait avant la class Video
    category = models.ForeignKey("Category", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, null=True)

    objects = VideoManager()

    class Meta:
        unique_together = ('slug', 'category')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # try/except car une video n'a pas de category par default (null=True)
        try:
            #return reverse('video_detail', kwargs={"id_a": self.id, "cat_slug": self.category.slug})
            return reverse('video_detail', kwargs={"vid_slug": self.slug, "cat_slug": self.category.slug})
        except:
            return "/"

    def get_share_message(self):
        full_url = "{}{}".format(settings.FULL_DOMAIN_NAME, self.get_absolute_url())
        return urlquote("{}: {}".format(self.share_message, full_url))

    def get_share_link(self):
        full_url = "{}{}".format(settings.FULL_DOMAIN_NAME, self.get_absolute_url())
        return full_url

    # def get_next_url(self):
    #     current_category = self.category
    #     videos = current_category.video_set.all().filter(order__gt=self.order)
    #     next_vid = None
    #     if len(videos) >= 1:
    #         try:
    #             next_vid = videos[0].get_absolute_url()
    #         except IndexError:
    #             next_vid = None
    #     return next_vid

    # def get_previous_url(self):
    #     current_category = self.category
    #     videos = current_category.video_set.all().filter(order__lt=self.order).reverse()
    #     previous_vid = None
    #     if len(videos) >= 1:
    #         try:
    #             previous_vid = videos[0].get_absolute_url()
    #         except IndexError:
    #             previous_vid = None
    #     return previous_vid


    # On a créé la fonction get_vid_for_direction qui peut servir dans les 2 cas, et qu'on a placé dans le utils.py,
    # car la fonction ne faisait pas parti des models

    def get_next_url(self):
        video = get_vid_for_direction(self, "next")
        if video is not None:
            return video.get_absolute_url()
        return None

    def get_previous_url(self):
        video = get_vid_for_direction(self, "previous")
        if video is not None:
            return video.get_absolute_url()
        return None

    @property
    def has_preview(self):
        if self.free_preview:
            return True
        else:
            return False


def video_signal_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        slug_title = slugify(instance.title)
        new_slug = "{} {} {}".format(instance.title, instance.category.slug, instance.id)
        try:
            obj_exists = Video.objects.get(slug=slug_title, category=instance.category)
            instance.slug = slugify(new_slug)
            instance.save()
            print('model exists, new slug generated')
        except Video.DoesNotExist:
            instance.slug = slug_title
            instance.save()
            print('slug and model created')
        except Video.MultipleObjectsReturned:
            instance.slug = slugify(new_slug)
            instance.save()
            print('multiple models exists, new slug generated')
        except:
            pass

post_save.connect(video_signal_post_save_receiver, sender=Video)


class CategoryQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def get_featured(self):
        # Video.objects.filter(featured=True)
        #return super(VideoManager, self).filter(featured=True)
        return self.get_queryset().active().featured()

    def all(self):
        return self.get_queryset().active()


class Category(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(default='abc', unique=True)
    #videos = models.ManyToManyField(Video, null=True, blank=True)
    description = models.TextField(max_length=5000, null=True, blank=True)
    tags = GenericRelation("TaggedItem", null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = CategoryManager()

    class Meta:
        ordering = ['title', 'timestamp']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={"cat_slug": self.slug})

    def get_image_url(self):
        return "{}{}".format(settings.MEDIA_URL, self.image)



TAG_CHOICES = (
    ("python", "python"),
    ("django", "django"),
    ("css", "css"),
    ("bootstrap", "bootstrap"),
)


class TaggedItem(models.Model):
    #category = models.ForeignKey(Category, null=True)
    #video = models.ForeignKey(Video)
    tag = models.SlugField(choices=TAG_CHOICES)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.tag





