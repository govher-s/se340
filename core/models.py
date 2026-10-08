from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

from .decorators.base import BasicPostAnalyzer
from .decorators.links import ExternalLinkDecorator
from .decorators.length import LengthDecorator
from .decorators.explicit import ExplicitLanguageDecorator

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(default=timezone.now)
    is_hidden = models.BooleanField(default=False)

    # results
    has_explicit_langauge = models.BooleanField(default=False)
    is_long_read = models.BooleanField(default=False)
    has_external_links = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            candidate = base_slug
            suffix = 2
            while type(self).objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = candidate

        update_fields = kwargs.get("update_fields")
        content_changed = self.pk is None
        if self.pk is not None and update_fields is None:
            previous_content = type(self).objects.only("content").get(pk=self.pk).content
            content_changed = previous_content != self.content
        should_analyze = content_changed or (update_fields is not None and "content" in update_fields)
        if should_analyze:
            analyzer = BasicPostAnalyzer(self.content)
            analyzer = ExternalLinkDecorator(analyzer)
            analyzer = LengthDecorator(analyzer)
            analyzer = ExplicitLanguageDecorator(analyzer)
            results = analyzer.analyze()
            self.has_explicit_langauge = results["has_explicit_language"]
            self.is_long_read = results["is_long_read"]
            self.has_external_links = results["has_external_links"]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:post_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title