from django.test import TestCase

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