#!/usr/bin/env python3
"""
DDD Documentation Verification Tool

Validates technical elements of documentation to prevent drift and catch issues.

Usage:
    tools/verify-docs              # Run all checks
    tools/verify-docs --verbose    # Detailed output
    tools/verify-docs --check json # Run specific check

Exit codes:
    0 = All checks passed
    1 = One or more checks failed
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Tuple, Dict
import argparse

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def color(text: str, color_code: str) -> str:
    """Add color to text if stdout is a TTY."""
    if sys.stdout.isatty():
        return f"{color_code}{text}{Colors.RESET}"
    return text

# Get repository root
REPO_ROOT = Path(__file__).parent.parent.resolve()

class VerificationResults:
    """Track verification results."""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.todos = []
    
    def add_pass(self, check: str, message: str = ""):
        self.passed.append((check, message))
    
    def add_fail(self, check: str, message: str):
        self.failed.append((check, message))
    
    def add_warning(self, check: str, message: str):
        self.warnings.append((check, message))
    
    def add_todo(self, message: str):
        self.todos.append(message)
    
    def print_summary(self):
        """Print verification summary."""
        print(f"\n{color('=' * 70, Colors.BOLD)}")
        print(f"{color('VERIFICATION SUMMARY', Colors.BOLD)}")
        print(f"{color('=' * 70, Colors.BOLD)}\n")
        
        # Passed checks
        if self.passed:
            print(f"{color('✓', Colors.GREEN)} {color('PASSED', Colors.GREEN)} ({len(self.passed)} checks)")
            for check, msg in self.passed:
                print(f"  • {check}")
                if msg:
                    print(f"    {msg}")
        
        # Warnings
        if self.warnings:
            print(f"\n{color('⚠', Colors.YELLOW)} {color('WARNINGS', Colors.YELLOW)} ({len(self.warnings)})")
            for check, msg in self.warnings:
                print(f"  • {check}")
                print(f"    {msg}")
        
        # Failed checks
        if self.failed:
            print(f"\n{color('✗', Colors.RED)} {color('FAILED', Colors.RED)} ({len(self.failed)} checks)")
            for check, msg in self.failed:
                print(f"  • {check}")
                print(f"    {msg}")
        
        # TODOs
        if self.todos:
            print(f"\n{color('📋', Colors.BLUE)} {color('TODOs CREATED', Colors.BLUE)} ({len(self.todos)})")
            for todo in self.todos:
                print(f"  • {todo}")
        
        # Final status
        print(f"\n{color('=' * 70, Colors.BOLD)}")
        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0
        
        if self.failed:
            print(f"{color('RESULT: FAILED', Colors.RED)} ({pass_rate:.0f}% passed)")
            print(f"{color('=' * 70, Colors.BOLD)}\n")
            return False
        else:
            print(f"{color('RESULT: PASSED', Colors.GREEN)} (All checks passed!)")
            print(f"{color('=' * 70, Colors.BOLD)}\n")
            return True

results = VerificationResults()

# ============================================================================
# CHECK 1: JSON Validity
# ============================================================================

def check_json_validity():
    """Verify all JSON files in the repository parse correctly."""
    print(f"\n{color('→ Checking JSON validity...', Colors.BLUE)}")
    
    json_files = [
        'CONFIG_REFERENCE.md',  # Contains JSON examples
        'FILTERS.md',            # Contains JSON examples
        'README.md',             # Contains JSON examples
        'examples/hello-world/.ddd/config.json',
        'templates/parasitic.json',
        'devbox.json',
    ]
    
    errors = []
    
    # Check actual JSON files
    for json_path in ['examples/hello-world/.ddd/config.json', 'templates/parasitic.json', 'devbox.json']:
        full_path = REPO_ROOT / json_path
        if not full_path.exists():
            errors.append(f"Missing file: {json_path}")
            continue
        
        try:
            with open(full_path) as f:
                json.load(f)
            print(f"  ✓ {json_path}")
        except json.JSONDecodeError as e:
            errors.append(f"{json_path}: {e}")
            print(f"  ✗ {json_path}: {e}")
    
    # Extract and validate JSON from markdown code blocks
    for md_file in ['CONFIG_REFERENCE.md', 'FILTERS.md', 'README.md']:
        full_path = REPO_ROOT / md_file
        if not full_path.exists():
            continue
        
        content = full_path.read_text()
        # Find JSON code blocks
        json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
        
        for i, block in enumerate(json_blocks):
            # Skip blocks with comments (not valid JSON but used for documentation)
            if '"_comment"' in block or '"comment"' in block:
                continue
            
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                errors.append(f"{md_file} JSON block #{i+1}: {e}")
    
    if errors:
        results.add_fail("JSON Validity", "\n".join(errors))
        for error in errors:
            results.add_todo(f"Fix JSON error: {error}")
    else:
        results.add_pass("JSON Validity", "All JSON is valid")

# ============================================================================
# CHECK 2: File References
# ============================================================================

def check_file_references():
    """Verify all file paths mentioned in docs actually exist."""
    print(f"\n{color('→ Checking file references...', Colors.BLUE)}")
    
    docs = ['README.md', 'CONFIG_REFERENCE.md', 'FILTERS.md', 'examples/README.md', 
            'examples/hello-world/README.md', 'PARASITIC_MODE.md']
    
    missing = []
    
    # Patterns for file references
    patterns = [
        r'`([^`]+\.(py|sh|json|md|c|txt|log))`',  # Backtick files
        r'\[.*?\]\(([^)]+\.(py|sh|json|md|c|txt))\)',  # Markdown links to files
    ]
    
    for doc in docs:
        doc_path = REPO_ROOT / doc
        if not doc_path.exists():
            missing.append(f"Documentation file missing: {doc}")
            continue
        
        content = doc_path.read_text()
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                file_ref = match.group(1)
                
                # Skip external URLs
                if file_ref.startswith('http'):
                    continue
                
                # Skip placeholders and examples
                if any(x in file_ref for x in ['<', '>', 'your', 'example', 'path/to']):
                    continue
                
                # Handle relative paths
                if file_ref.startswith('./'):
                    check_path = doc_path.parent / file_ref[2:]
                elif file_ref.startswith('../'):
                    check_path = doc_path.parent / file_ref
                else:
                    check_path = REPO_ROOT / file_ref
                
                if not check_path.exists():
                    missing.append(f"{doc} references missing file: {file_ref}")
    
    if missing:
        results.add_fail("File References", "\n".join(missing[:10]))  # Limit output
        for ref in missing[:5]:  # Only create TODOs for first 5
            results.add_todo(f"Fix file reference: {ref}")
    else:
        results.add_pass("File References", "All referenced files exist")

# ============================================================================
# CHECK 3: Internal Links
# ============================================================================

def check_internal_links():
    """Verify all internal markdown links point to existing files."""
    print(f"\n{color('→ Checking internal links...', Colors.BLUE)}")
    
    docs = list(REPO_ROOT.glob('*.md')) + list(REPO_ROOT.glob('examples/**/*.md'))
    broken = []
    
    for doc in docs:
        content = doc.read_text()
        
        # Find markdown links [text](url)
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            link = match.group(2)
            
            # Skip external links
            if link.startswith('http'):
                continue
            
            # Skip anchors only
            if link.startswith('#'):
                continue
            
            # Remove anchors from path
            link = link.split('#')[0]
            
            # Skip empty links
            if not link:
                continue
            
            # Resolve relative to doc location
            if link.startswith('./'):
                target = doc.parent / link[2:]
            elif link.startswith('../'):
                target = doc.parent / link
            else:
                target = doc.parent / link
            
            if not target.exists():
                rel_doc = doc.relative_to(REPO_ROOT)
                broken.append(f"{rel_doc} → {link}")
    
    if broken:
        results.add_fail("Internal Links", "\n".join(broken[:10]))
        for link in broken[:5]:
            results.add_todo(f"Fix broken link: {link}")
    else:
        results.add_pass("Internal Links", "All internal links valid")

# ============================================================================
# CHECK 4: Code Block Syntax
# ============================================================================

def check_code_blocks():
    """Verify all code blocks have language tags."""
    print(f"\n{color('→ Checking code block syntax...', Colors.BLUE)}")
    
    docs = list(REPO_ROOT.glob('*.md')) + list(REPO_ROOT.glob('examples/**/*.md'))
    missing_lang = []
    
    for doc in docs:
        content = doc.read_text()
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.strip() == '```':
                rel_doc = doc.relative_to(REPO_ROOT)
                missing_lang.append(f"{rel_doc}:{i+1} - Code block without language tag")
    
    if missing_lang:
        results.add_warning("Code Block Syntax", "\n".join(missing_lang[:10]))
        for item in missing_lang[:3]:
            results.add_todo(f"Add language tag to: {item}")
    else:
        results.add_pass("Code Block Syntax", "All code blocks have language tags")

# ============================================================================
# CHECK 5: Example Build Test
# ============================================================================

def check_example_builds():
    """Verify examples actually build."""
    print(f"\n{color('→ Checking example builds...', Colors.BLUE)}")
    
    hello_world = REPO_ROOT / 'examples' / 'hello-world'
    
    if not hello_world.exists():
        results.add_fail("Example Builds", "examples/hello-world/ does not exist")
        results.add_todo("Create examples/hello-world/ directory")
        return
    
    # Check required files
    required = ['hello.c', 'Makefile', '.ddd/config.json', 'README.md']
    missing = [f for f in required if not (hello_world / f).exists()]
    
    if missing:
        results.add_fail("Example Builds", f"Missing files: {', '.join(missing)}")
        for f in missing:
            results.add_todo(f"Create examples/hello-world/{f}")
        return
    
    # Try to build
    try:
        os.chdir(hello_world)
        subprocess.run(['make', 'clean'], capture_output=True, check=True, timeout=5)
        result = subprocess.run(['make'], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            results.add_pass("Example Builds", "hello-world compiles successfully")
            # Clean up
            subprocess.run(['make', 'clean'], capture_output=True)
        else:
            results.add_fail("Example Builds", f"make failed:\n{result.stderr}")
            results.add_todo("Fix hello-world build errors")
    except subprocess.TimeoutExpired:
        results.add_fail("Example Builds", "Build timed out")
        results.add_todo("Investigate hello-world build timeout")
    except FileNotFoundError:
        results.add_warning("Example Builds", "make not found (skipping build test)")
    except Exception as e:
        results.add_fail("Example Builds", f"Build error: {e}")
        results.add_todo(f"Fix hello-world build: {e}")
    finally:
        os.chdir(REPO_ROOT)

# ============================================================================
# CHECK 6: Required Sections
# ============================================================================

def check_required_sections():
    """Verify key documentation has required sections."""
    print(f"\n{color('→ Checking required sections...', Colors.BLUE)}")
    
    requirements = {
        'README.md': [
            'Overview',
            'Quick Start',
            'Prerequisites',
            'Installation',
            'Usage',
            'Documentation',
        ],
        'CONFIG_REFERENCE.md': [
            'Basic Structure',
            'Examples',
        ],
        'FILTERS.md': [
            'Built-in Filters',
            'Creating Custom Filters',
        ],
    }
    
    missing = []
    
    for doc, sections in requirements.items():
        doc_path = REPO_ROOT / doc
        if not doc_path.exists():
            missing.append(f"{doc}: File does not exist")
            continue
        
        content = doc_path.read_text()
        
        for section in sections:
            # Check for section header (## or ###)
            if not re.search(f'^##+ .*{re.escape(section)}', content, re.MULTILINE | re.IGNORECASE):
                missing.append(f"{doc}: Missing section '{section}'")
    
    if missing:
        results.add_fail("Required Sections", "\n".join(missing))
        for item in missing:
            results.add_todo(f"Add missing section: {item}")
    else:
        results.add_pass("Required Sections", "All required sections present")

# ============================================================================
# CHECK 7: Config Schema Validation
# ============================================================================

def check_config_schema():
    """Verify configs match expected schema."""
    print(f"\n{color('→ Checking config schema...', Colors.BLUE)}")
    
    required_keys = {
        'targets': dict,
    }
    
    configs = [
        'examples/hello-world/.ddd/config.json',
    ]
    
    errors = []
    
    for config_path in configs:
        full_path = REPO_ROOT / config_path
        if not full_path.exists():
            errors.append(f"{config_path}: File does not exist")
            continue
        
        try:
            with open(full_path) as f:
                config = json.load(f)
            
            # Check required keys
            for key, expected_type in required_keys.items():
                if key not in config:
                    errors.append(f"{config_path}: Missing required key '{key}'")
                elif not isinstance(config[key], expected_type):
                    errors.append(f"{config_path}: '{key}' should be {expected_type.__name__}")
            
            # Check targets structure
            if 'targets' in config:
                if 'dev' not in config['targets']:
                    results.add_warning("Config Schema", 
                        f"{config_path}: No 'dev' target (daemon currently hardcoded to 'dev')")
                
                for target_name, target in config['targets'].items():
                    if 'build' not in target:
                        errors.append(f"{config_path}: Target '{target_name}' missing 'build' stage")
        
        except json.JSONDecodeError:
            errors.append(f"{config_path}: Invalid JSON (caught by JSON validity check)")
    
    if errors:
        results.add_fail("Config Schema", "\n".join(errors))
        for error in errors:
            results.add_todo(f"Fix config schema: {error}")
    else:
        results.add_pass("Config Schema", "All configs match expected schema")

# ============================================================================
# CHECK 8: Version Consistency
# ============================================================================

def check_version_consistency():
    """Verify version numbers are consistent across files."""
    print(f"\n{color('→ Checking version consistency...', Colors.BLUE)}")
    
    # Read VERSION file
    version_file = REPO_ROOT / 'VERSION'
    if not version_file.exists():
        results.add_fail("Version Consistency", "VERSION file does not exist")
        results.add_todo("Create VERSION file")
        return
    
    version = version_file.read_text().strip()
    
    # Check mentions in key files
    files_to_check = {
        'README.md': f'v{version}',
        'src/dd-daemon.py': f'v{version}',
    }
    
    mismatches = []
    
    for file_path, expected in files_to_check.items():
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            content = full_path.read_text()
            if expected not in content:
                mismatches.append(f"{file_path}: Expected version '{expected}' not found")
    
    if mismatches:
        results.add_warning("Version Consistency", "\n".join(mismatches))
        for mismatch in mismatches:
            results.add_todo(f"Update version: {mismatch}")
    else:
        results.add_pass("Version Consistency", f"All files reference v{version}")

# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Verify DDD documentation')
    parser.add_argument('--check', help='Run specific check only')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    print(f"{color('=' * 70, Colors.BOLD)}")
    print(f"{color('DDD DOCUMENTATION VERIFICATION', Colors.BOLD)}")
    print(f"{color('=' * 70, Colors.BOLD)}")
    print(f"\nRepository: {REPO_ROOT}")
    
    # Run checks
    checks = {
        'json': check_json_validity,
        'files': check_file_references,
        'links': check_internal_links,
        'code-blocks': check_code_blocks,
        'examples': check_example_builds,
        'sections': check_required_sections,
        'schema': check_config_schema,
        'version': check_version_consistency,
    }
    
    if args.check:
        if args.check in checks:
            checks[args.check]()
        else:
            print(f"Unknown check: {args.check}")
            print(f"Available: {', '.join(checks.keys())}")
            return 1
    else:
        # Run all checks
        for check_func in checks.values():
            check_func()
    
    # Print summary
    success = results.print_summary()
    
    # Write TODOs to file if any found
    if results.todos:
        todo_file = REPO_ROOT / 'DOCS_VERIFICATION_TODOS.md'
        with open(todo_file, 'w') as f:
            f.write("# Documentation Verification TODOs\n\n")
            f.write("Issues found by `tools/verify-docs`:\n\n")
            for i, todo in enumerate(results.todos, 1):
                f.write(f"{i}. {todo}\n")
        print(f"\n{color('→', Colors.BLUE)} TODOs written to: {todo_file.relative_to(REPO_ROOT)}")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
