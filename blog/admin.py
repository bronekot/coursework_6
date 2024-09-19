from django.contrib import admin
from django.utils import timezone

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "views")
    list_filter = ("published_at", "author")
    search_fields = ("title", "content")
    date_hierarchy = "created_at"
    actions = ["publish_posts"]

    def publish_posts(self, request, queryset):
        updated = queryset.update(published_at=timezone.now())
        self.message_user(request, f"{updated}  были успешно опубликованы.")

    publish_posts.short_description = "Опубликовать выбранные "

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Если это новый объект
            obj.author = request.user
        super().save_model(request, obj, form, change)
        super().save_model(request, obj, form, change)
