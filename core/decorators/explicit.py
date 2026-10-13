import string

from better_profanity import profanity
from .base import PostAnalyzerDecorator


class ExplicitLanguageDecorator(PostAnalyzerDecorator):

    def analyze(self):
        results = super().analyze()

        if profanity.contains_profanity(self.content):
            results["has_explicit_language"] = True

        return results