from . import register_filter
from .base import BaseFilter
import re

@register_filter("gcc_make")
class GccMakeFilter(BaseFilter):
    def __init__(self, config=None):
        super().__init__(config)
        # Use the config to determine what path prefix to strip
        self.strip_prefix = self.config.get("path_strip", "")
        self.context_lines = 0
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def process(self, text: str) -> str:
        # 1. Strip ANSI
        text = self.ansi_escape.sub('', text)
        
        # 2. Strip Path Prefix (Normalization)
        if self.strip_prefix:
            text = text.replace(self.strip_prefix, "")

        lines = text.splitlines()
        output = []

        for line in lines:
            # A. Detect Critical Signals
            if any(k in line.lower() for k in ["error:", "warning:", "fatal:", "note:"]):
                self.context_lines = 5  # Open the gate
                output.append(line)
                continue

            # B. Handle Context
            if self.context_lines > 0:
                output.append(line)
                self.context_lines -= 1
                continue

            # C. Filter Noise
            if "make[" in line or "Entering directory" in line or "Leaving directory" in line:
                continue
            
            # Default: Keep line if we aren't sure
            output.append(line)

        return "\n".join(output)
