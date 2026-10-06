from abc import ABC, abstractmethod


class PostAnalyzer(ABC):

    @property
    @abstractmethod
    def content(self):
        pass

    @abstractmethod
    def analyze(self):
        pass


class BasicPostAnalyzer(PostAnalyzer):

    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    def analyze(self):
        return {
            "has_explicit_language": False,
            "is_long_read": False,
            "has_external_links": False,
        }


class PostAnalyzerDecorator(PostAnalyzer):

    def __init__(self, analyzer):
        self.analyzer = analyzer

    @property
    def content(self):
        return self.analyzer.content

    def analyze(self):
        return self.analyzer.analyze()