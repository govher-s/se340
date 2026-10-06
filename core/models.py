from django.db import models
from django.conf import settings

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
    has_explicit_langauge = models.BooleanField(default=False)
    is_long_read = models.BooleanField(default=False)
    has_external_links = models.BooleanField(default=False)

    def __str__(self):
        return self.title