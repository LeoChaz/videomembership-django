from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
from .models import Video, Category, TaggedItem


class TaggedItemInLine(GenericTabularInline):
    model = TaggedItem

class VideoInLine(admin.TabularInline):
    model = Video

class VideoAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInLine]
    list_display = ["__str__", "slug"]
    prepopulated_fields = {"slug": ["title"]}
    class Meta:
        model = Video


class CategoryAdmin(admin.ModelAdmin):
    #inlines = [TaggedItemInLine, VideoInLine]
    class Meta:
        model = Category

admin.site.register(Video, VideoAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TaggedItem)







