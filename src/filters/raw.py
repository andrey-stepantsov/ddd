from . import register_filter
from .base import BaseFilter
import re

@register_filter("raw")
class RawFilter(BaseFilter):
    def process(self, text: str) -> str:
        # Standard ANSI stripping
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
