from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Post

from .decorators.base import BasicPostAnalyzer
from .decorators.links import ExternalLinkDecorator
from .decorators.length import LengthDecorator
from .decorators.explicit import ExplicitLanguageDecorator

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

class PostModelTest(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )

    def test_post_flags_are_set_when_saved(self):
        post = Post.objects.create(
            title="Test Trip",
            content="This trip was damn exhausting. Visit https://example.com",
            author=self.user
        )

        self.assertTrue(post.has_explicit_language)
        self.assertTrue(post.has_external_links)
        self.assertFalse(post.is_long_read)