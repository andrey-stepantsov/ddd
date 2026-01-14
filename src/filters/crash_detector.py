import re
import json
from . import register_filter
from .base import BaseFilter

@register_filter("crash_detector")
class CrashDetectorFilter(BaseFilter):
    def process(self, text):
        """
        Scans for high-priority crash signatures (Segfault, Core Dump, Aborted).
        Returns a JSON error object immediately if found.
        """
        # Common crash signatures in C/C++ output
        # Case insensitive match for safety
        crash_patterns = [
            r"Segmentation fault",
            r"core dumped",
            r"Aborted \(core dumped\)",
            r"Bus error",
            r"Assertion .* failed"
        ]
        
        combined_regex = "|".join(crash_patterns)
        match = re.search(combined_regex, text, re.IGNORECASE | re.MULTILINE)
        
        if match:
            # We found a crash!
            crash_entry = {
                "file": "CRITICAL_RUNTIME_FAILURE",
                "line": 0,
                "type": "fatal",
                "message": f"Process Crashed: '{match.group(0)}'. Output may be truncated."
            }
            
            # ATTEMPT 1: Parse as pure JSON
            data = None
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # ATTEMPT 2: Parse as JSON prefix (handling trailing garbage)
                try:
                    data, _ = json.JSONDecoder().raw_decode(text)
                except json.JSONDecodeError:
                    pass

            # If we successfully salvaged a list, prepend our crash error
            if isinstance(data, list):
                data.insert(0, crash_entry) # Top priority
                return json.dumps(data, indent=2)
                
            # Fallback: Return just this error
            return json.dumps([crash_entry], indent=2)

        return text
