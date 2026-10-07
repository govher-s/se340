import string

from .base import PostAnalyzerDecorator


class ExplicitLanguageDecorator(PostAnalyzerDecorator):

    def analyze(self):
        results = super().analyze()

        explicit_words = [
            "damn",
            "hell",
            "shit",
            "fuck",
        ]

        words = [
            word.strip(string.punctuation)
            for word in self.content.lower().split()
        ]

        if any(word in explicit_words for word in words):
            results["has_explicit_language"] = True

        return results