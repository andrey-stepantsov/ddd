import re
import json
from . import register_filter
from .base import BaseFilter

@register_filter("gcc_json")
class GccJsonFilter(BaseFilter):
    def process(self, text):
        """
        Parses GCC/Clang output into a JSON list of error objects.
        Input: Standard compiler output.
        Output: JSON String.
        """
        results = []
        
        # Regex for: main.c:10:5: error: expected ';'
        # Group 1: Filename
        # Group 2: Line
        # Group 3: Column (Optional)
        # Group 4: Type (error/warning)
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
            
        # --- CRITICAL FIX: Silent Failure Detection ---
        # If text exists but no standard errors were found, the build might have 
        # failed due to Linker errors, Missing Makefiles, or Segmentation faults.
        # We inject a synthetic error so the AI knows something is wrong.
        if not results and text.strip():
            # Check for common failure keywords to avoid false positives on success logs
            # If the log is just "Nothing to be done", we shouldn't error.
            # But usually this filter is used when things go WRONG.
            # We take a safe approach: capture the first few lines of raw output.
            results.append({
                "file": "build.log",
                "line": 0,
                "type": "error",
                "message": f"Build Output (Unparseable):\n{text.strip()[:1000]}"
            })

        # Return indented JSON for readability (AI can read it fine, humans too)
        return json.dumps(results, indent=2)