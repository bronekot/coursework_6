from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts"
    )

    def __str__(self):
        return self.title

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    class Meta:
        ordering = ["-published_at"]


@receiver([post_save, post_delete], sender=BlogPost)
def clear_blog_cache(sender, instance, **kwargs):
    cache.clear()
