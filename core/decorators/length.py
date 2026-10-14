from .base import PostAnalyzerDecorator

class LengthDecorator(PostAnalyzerDecorator):

    def analyze(self):
        results = super().analyze()

        word_count = len(self.content.split())

        if word_count > 1500:
            results["is_long_read"] = True

        return results