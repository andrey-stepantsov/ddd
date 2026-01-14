import re
import json
from . import register_filter
from .base import BaseFilter

@register_filter("gcc_json")
class GccJsonFilter(BaseFilter):
    def process(self, text):
        """
        Parses GCC/Clang output into a JSON list of error objects.
        Patched to allow 'Nothing to be done' as success.
        """
        results = []
        
        # Regex for: main.c:10:5: error: expected ';'
        # Group 1: Filename
        # Group 2: Line
        # Group 3: Column (Optional)
        # Group 4: Type (error/warning/note)
        # Group 5: Message
        regex = re.compile(r"^([^:\n]+):(\d+):(?:(\d+):)?\s*(error|warning|note):\s*(.+)$", re.MULTILINE)
        
        for match in regex.finditer(text):
            entry = {
                "file": match.group(1),
                "line": int(match.group(2)),
                "type": match.group(4),
                "message": match.group(5).strip()
            }
            # Add column if present
            if match.group(3):
                entry["col"] = int(match.group(3))
                
            results.append(entry)
            
        # --- SILENT FAILURE DETECTION (PATCHED) ---
        if not results and text.strip():
            # FIX: If we see success markers, return empty list (Success)
            # instead of triggering the silent failure detector.
            if "Nothing to be done" in text or "Build finished" in text:
                return json.dumps([])

            # Otherwise, assume it's a crash (Segfault, Linker error, etc)
            results.append({
                "file": "build.log",
                "line": 0,
                "type": "error",
                "message": f"Build Output (Unparseable):\n{text.strip()[:1000]}"
            })

        return json.dumps(results, indent=2)
