class BaseFilter:
    def __init__(self, config=None):
        self.config = config or {}
    def process(self, text: str) -> str:
        return text
