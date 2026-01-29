# Documentation Verification Tool

Automated checks to ensure DDD documentation stays accurate and consistent.

## Purpose

Prevents documentation drift by verifying:
- JSON configs are valid
- File paths exist
- Internal links work
- Code blocks have language tags
- Examples build successfully
- Required sections present
- Version numbers consistent

## Usage

### Run All Checks

```bash
tools/verify-docs
```

### Run Specific Check

```bash
tools/verify-docs --check json        # JSON validity only
tools/verify-docs --check examples    # Build tests only
tools/verify-docs --check links       # Link validation only
```

### Available Checks

- `json` - Validate all JSON files and JSON code blocks
- `files` - Verify file references in docs exist
- `links` - Check internal markdown links
- `code-blocks` - Ensure code blocks have language tags
- `examples` - Build hello-world example
- `sections` - Verify required documentation sections
- `schema` - Validate config.json structure
- `version` - Check version consistency

### Verbose Output

```bash
tools/verify-docs --verbose
```

## Exit Codes

- `0` - All checks passed
- `1` - One or more checks failed

## CI Integration

Add to `.github/workflows/verify-docs.yml`:

```yaml
name: Verify Documentation

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Verify docs
        run: tools/verify-docs
```

## What Gets Checked

### 1. JSON Validity
- All `.json` files parse correctly
- JSON code blocks in markdown are valid
- Ignores commented JSON (documentation examples)

### 2. File References
- Paths mentioned in backticks exist
- Linked files (`.py`, `.sh`, `.md`, etc.) exist
- Skips placeholders and external URLs

### 3. Internal Links
- All `[text](link.md)` point to real files
- Handles relative paths correctly
- Skips external URLs and anchors

### 4. Code Block Syntax
- All code blocks have language tags
- Warns if ` ``` ` found without language

### 5. Example Builds
- `examples/hello-world/` compiles with `make`
- Required files present
- Build succeeds without errors

### 6. Required Sections
- README.md has Overview, Quick Start, Installation, etc.
- CONFIG_REFERENCE.md has examples
- FILTERS.md has filter documentation

### 7. Config Schema
- `.ddd/config.json` files have required keys
- `targets` structure is valid
- Warns if 'dev' target missing (currently hardcoded)

### 8. Version Consistency
- VERSION file matches references in docs
- README and daemon show same version

## Output Format

```
==================================================
DDD DOCUMENTATION VERIFICATION
==================================================

→ Checking JSON validity...
  ✓ examples/hello-world/.ddd/config.json
  ✓ templates/parasitic.json

→ Checking file references...
  ✓ All referenced files exist

...

==================================================
VERIFICATION SUMMARY
==================================================

✓ PASSED (6 checks)
  • JSON Validity
  • File References
  • Internal Links
  • Example Builds
  • Required Sections
  • Config Schema

⚠ WARNINGS (1)
  • Code Block Syntax
    README.md:123 - Code block without language tag

📋 TODOs CREATED (1)
  • Add language tag to: README.md:123

==================================================
RESULT: PASSED (All checks passed!)
==================================================

→ TODOs written to: DOCS_VERIFICATION_TODOS.md
```

## Handling Failures

When checks fail, the tool:
1. Shows what failed and why
2. Creates `DOCS_VERIFICATION_TODOS.md` with action items
3. Returns exit code 1 (for CI)

**Do not commit fixes immediately** - review TODOs first to understand scope.

## Development

### Adding New Checks

Edit `tools/verify_docs.py`:

```python
def check_my_new_thing():
    """Verify something new."""
    print(f"\n{color('→ Checking my thing...', Colors.BLUE)}")
    
    if problem_found:
        results.add_fail("My Check", "Description of problem")
        results.add_todo("Fix: specific action item")
    else:
        results.add_pass("My Check", "Everything OK")

# Add to checks dict in main()
checks = {
    'my-thing': check_my_new_thing,
    # ...
}
```

### Testing the Tool

```bash
# Test specific check
tools/verify-docs --check json

# Test all checks
tools/verify-docs

# Verify TODOs file created
cat DOCS_VERIFICATION_TODOS.md
```

## Architecture

Uses the same bootstrap pattern as `dd-daemon` and `ddd-test`:

```
tools/verify-docs          # Bash wrapper (uses bootstrap.sh)
  └─→ bootstrap.sh         # Creates isolated Python venv
       └─→ verify_docs.py  # Main verification logic
```

Benefits:
- Works in CI (GitHub Actions)
- Works in devbox shell
- Works locally
- No Docker required
- Hermetic environment

## When to Run

### During Development
```bash
# Before committing doc changes
tools/verify-docs

# Quick check while editing
tools/verify-docs --check links
```

### In CI
- On every PR
- On push to main
- Before releases

### After Updates
- After changing examples
- After updating configs
- After restructuring docs
- After version bumps

## Troubleshooting

### "bootstrap.sh not found"
Run from repository root, not tools/ directory:
```bash
cd /path/to/ddd
tools/verify-docs
```

### "make: command not found"
Install build tools:
- macOS: `xcode-select --install`
- Ubuntu: `sudo apt install build-essential`
- Or skip with: `tools/verify-docs --check json` (skip build check)

### "Module not found"
Bootstrap.sh should handle dependencies. If issues:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### False Positives
If check incorrectly fails:
1. Check if file path is correct
2. Verify regex patterns in `verify_docs.py`
3. Add exception for special cases
4. Report issue with examples

## Maintenance

### Keep Checks Updated
- Add checks for new doc types
- Update schema validation as config evolves
- Adjust file patterns as project grows

### Review TODOs Regularly
- `DOCS_VERIFICATION_TODOS.md` tracks issues
- Triage: fix now vs document vs ignore
- Clear after addressing

### CI Integration
- Monitor CI runs for failures
- Update check thresholds if too noisy
- Add new checks for recurring issues

## Future Enhancements

Potential additions:
- [ ] External link validation (requires network)
- [ ] Spelling check (basic typo detection)
- [ ] Markdown linting (formatting consistency)
- [ ] Screenshot verification (if/when added)
- [ ] Performance benchmarks (doc build time)
- [ ] Coverage metrics (% of features documented)

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [README.md](../README.md) - Project overview
- [CONFIG_REFERENCE.md](../CONFIG_REFERENCE.md) - Config documentation
- [FILTERS.md](../FILTERS.md) - Filter documentation
