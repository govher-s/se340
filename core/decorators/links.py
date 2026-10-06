from .base import PostAnalyzerDecorator


class ExternalLinkDecorator(PostAnalyzerDecorator):

    def analyze(self):
        results = super().analyze()

        if "http://" in self.content or "https://" in self.content:
            results["has_external_links"] = True

        return results