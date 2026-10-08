from io import BytesIO

from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .decorators.base import BasicPostAnalyzer
from .decorators.links import ExternalLinkDecorator
from .decorators.length import LengthDecorator
from .decorators.explicit import ExplicitLanguageDecorator
from .models import Post

# Create your tests here.
class ExternalLinkDecoratorTest(TestCase):

    def test_post_with_external_link(self):
        post_content = "Check out my trip at https://example.com"

        analyzer = BasicPostAnalyzer(post_content)
        analyzer = ExternalLinkDecorator(analyzer)

        results = analyzer.analyze()

        self.assertTrue(results["has_external_links"])

class LengthDecoratorTest(TestCase):

    def test_short_post(self):
        post_content = "This is a short travel post."

        analyzer = BasicPostAnalyzer(post_content)
        analyzer = LengthDecorator(analyzer)

        results = analyzer.analyze()

        self.assertFalse(results["is_long_read"])

    def test_long_post(self):
        post_content = "travel " * 2001

        analyzer = BasicPostAnalyzer(post_content)
        analyzer = LengthDecorator(analyzer)

        results = analyzer.analyze()

        self.assertTrue(results["is_long_read"])

class ExplicitLanguageDecoratorTest(TestCase):

    def test_post_with_explicit_language(self):
        post_content = "That was a damn long flight"

        analyzer = BasicPostAnalyzer(post_content)
        analyzer = ExplicitLanguageDecorator(analyzer)

        results = analyzer.analyze()

        self.assertTrue(results["has_explicit_language"])

    def test_post_without_explicit_language(self):
        post_content = "That was a very long flight"

        analyzer = BasicPostAnalyzer(post_content)
        analyzer = ExplicitLanguageDecorator(analyzer)

        results = analyzer.analyze()

        self.assertFalse(results["has_explicit_language"])


class PostPageTests(TestCase):

    @staticmethod
    def create_test_image():
        image = Image.new("RGB", (2, 2), color="blue")
        image_file = BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        return SimpleUploadedFile(
            "upload-test.jpg",
            image_file.read(),
            content_type="image/jpeg",
        )

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(
            username="traveler",
            password="test-password",
        )
        cls.post = Post.objects.create(
            title="A Walk Through Venice",
            content="A short travel story.",
            author=user,
        )

    def test_home_page_renders(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_list_renders(self):
        response = self.client.get(reverse("core:post_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_detail_renders_at_slug_url(self):
        response = self.client.get(self.post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.content)

    def test_post_get_absolute_url_uses_slug(self):
        self.assertEqual(
            self.post.get_absolute_url(),
            f"/posts/{self.post.slug}/",
        )

    def test_home_page_searches_title(self):
        response = self.client.get(reverse("core:home"), {"q": "Venice"})

        self.assertContains(response, self.post.title)
        self.assertContains(response, 'value="Venice"')

    def test_post_list_searches_content(self):
        response = self.client.get(reverse("core:post_list"), {"q": "short travel"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_home_excludes_selected_analyzer_label(self):
        self.post.is_long_read = True
        self.post.save(update_fields=["is_long_read"])

        response = self.client.get(reverse("core:home"), {"exclude": "profanity"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, 'value="profanity"')

    def test_home_excludes_multiple_analyzer_labels(self):
        self.post.has_external_links = True
        self.post.save(update_fields=["has_external_links"])

        response = self.client.get(
            reverse("core:home"),
            [("exclude", "profanity"), ("exclude", "external-links")],
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post.title)

    def test_home_excludes_long_reads(self):
        self.post.is_long_read = True
        self.post.save(update_fields=["is_long_read"])

        response = self.client.get(reverse("core:home"), {"exclude": "long"})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post.title)

    def test_hidden_posts_are_not_displayed_in_home(self):
        self.post.is_hidden = True
        self.post.save(update_fields=["is_hidden"])

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post.title)

    def test_hidden_posts_are_not_displayed_in_post_list(self):
        self.post.is_hidden = True
        self.post.save(update_fields=["is_hidden"])

        response = self.client.get(reverse("core:post_list"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.post.title)

    def test_manual_long_read_flag_survives_post_save(self):
        self.post.is_long_read = True
        self.post.save()

        self.assertTrue(Post.objects.get(pk=self.post.pk).is_long_read)

    def test_authenticated_user_can_create_post_with_image(self):
        self.client.force_login(self.post.author)
        response = self.client.post(
            reverse("core:create_post"),
            {
                "title": "Uploaded Story",
                "content": "A story with https://example.com",
                "image": self.create_test_image(),
            },
        )

        self.assertRedirects(response, reverse("core:home"))
        uploaded_post = Post.objects.get(title="Uploaded Story")
        self.assertEqual(uploaded_post.author, self.post.author)
        self.assertTrue(uploaded_post.image.name.startswith("post_images/upload-test"))
        self.assertTrue(uploaded_post.image.name.endswith(".jpg"))
        self.assertTrue(uploaded_post.has_external_links)