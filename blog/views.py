from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView

from .models import BlogPost


@method_decorator(cache_page(60 * 15), name="dispatch")
class BlogListView(ListView):
    model = BlogPost
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(published_at__isnull=False)


@method_decorator(cache_page(60 * 15), name="dispatch")
class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj
        return obj
