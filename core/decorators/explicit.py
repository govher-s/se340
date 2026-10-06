from .base import PostAnalyzerDecorator

class ExplicitLanguageDecorator(PostAnalyzerDecorator):

    def analyze(self):
        results = super().analyze()

        explicit_words = ["damn", "hell", "shit", "fuck"]

        words = self.content.lower().split()

        for word in explicit_words:
            if word in words:
                results["has_explicit_language"] = True
                break

        return results