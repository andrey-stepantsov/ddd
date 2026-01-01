class BaseFilter:
    def __init__(self, config=None):
        self.config = config or {}

    def process(self, text: str) -> str:
        """Process the text and return the cleaned version."""
        return text
