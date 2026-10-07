from django.db import models
from django.conf import settings
from django.db import models

from .decorators.base import BasicPostAnalyzer
from .decorators.links import ExternalLinkDecorator
from .decorators.length import LengthDecorator
from .decorators.explicit import ExplicitLanguageDecorator

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # results
    has_explicit_language = models.BooleanField(default=False)
    is_long_read = models.BooleanField(default=False)
    has_external_links = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        analyzer = BasicPostAnalyzer(self.content)

        analyzer = ExternalLinkDecorator(analyzer)
        analyzer = LengthDecorator(analyzer)
        analyzer = ExplicitLanguageDecorator(analyzer)

        results = analyzer.analyze()

        print("CONTENT:", self.content)
        print("RESULTS:", results)

        self.has_explicit_language = results["has_explicit_language"]
        self.is_long_read = results["is_long_read"]
        self.has_external_links = results["has_external_links"]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title