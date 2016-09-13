from django.contrib import admin

from .models import PageView


class PageViewAdmin(admin.ModelAdmin):
    list_display = ["__str__", "timestamp"]

    class Meta:
        model = PageView

# Register your models here.
admin.site.register(PageView, PageViewAdmin)