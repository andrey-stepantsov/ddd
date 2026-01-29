# Documentation Verification TODOs

**Generated:** January 28, 2026  
**Tool:** `tools/verify-docs`  
**Status:** 24 issues found (3 checks failed, 1 warning)

---

## Summary

| Category | Count | Severity |
|----------|-------|----------|
| JSON Errors | 11 | 🔴 High |
| File References | 5 | 🟡 Medium |
| Broken Links | 5 | 🟢 Low |
| Missing Language Tags | 3 | 🟢 Low |

---

## 🔴 High Priority: JSON Errors (11)

These are in **documentation examples** (not actual config files). The JSON blocks contain explanatory text that makes them invalid JSON but helpful for documentation.

### CONFIG_REFERENCE.md (7 issues)
1. JSON block #1: Expecting property name enclosed in double quotes
2. JSON block #2: Extra data (inline comments)
3. JSON block #3: Extra data (inline comments)
4. JSON block #4: Extra data (inline comments)
5. JSON block #5: Extra data (inline comments)
6. JSON block #6: Extra data (inline comments)
7. JSON block #13: Extra data (inline comments)

**Root cause:** Using `json` language tag for blocks with comments/explanations  
**Fix:** Change language tag from `json` to `jsonc` or `javascript` for commented examples  
**Impact:** Low - Examples are illustrative, not meant to be copy-pasted

### README.md (4 issues)
8. JSON block #1: Extra data (config with comments)
9. JSON block #3: Extra data (filter example)
10. JSON block #4: Extra data (filter example)
11. JSON block #5: Extra data (filter example)

**Root cause:** Same as above  
**Fix:** Use `jsonc` for examples with inline explanations  
**Impact:** Low - Quick Start examples work, these are illustrative

---

## 🟡 Medium Priority: File References (5)

These are command examples in docs that reference files that don't exist in repo root (they exist in user projects).

### README.md (5 issues)
12. `cat .ddd/daemon.log` - Example command, not a file to check
13. `cat .ddd/run/last_build.raw.log` - Example command
14. `build.log` - Referenced as artifact name
15. `.ddd/config.json` - Referenced in user project context
16. `config.json` - Referenced in user project context

**Root cause:** Tool treats backticked text as file references  
**Fix:** Update regex in `verify_docs.py` to skip command examples  
**Alternative:** Accept these as false positives (not actual issues)  
**Impact:** Low - These are intentionally showing user-side paths

---

## 🟢 Low Priority: Broken Links (5)

Links to **planned content** that doesn't exist yet.

### PLAN_NEW_USER_IMPROVEMENTS.md (5 issues)
17. `hello-world/` - Links to planned example directory structure
18. `python-pytest/` - Phase 2 content (not yet created)
19. `multi-stage/` - Phase 2 content (not yet created)
20. `QUICKSTART.md` - Phase 2 content (not yet created)
21. `TROUBLESHOOTING.md` - Phase 3 content (not yet created)

**Root cause:** Planning doc references future work  
**Fix:** Either:
- Create placeholder files
- Mark as "Coming Soon" with text instead of links
- Ignore (planning docs don't need valid links)  
**Impact:** None - PLAN_NEW_USER_IMPROVEMENTS.md is not user-facing

### SESSION_SUMMARY.md (ignored, local file)

---

## 🟢 Low Priority: Missing Language Tags (3)

Code blocks without language specification.

### PLAN_NEW_USER_IMPROVEMENTS.md (3 issues)
22. Line 43 - Code block without language tag
23. Line 51 - Code block without language tag
24. Line 57 - Code block without language tag

**Root cause:** Planning doc uses generic code blocks  
**Fix:** Add appropriate language tags (bash, json, markdown)  
**Impact:** None - Planning doc is not user-facing

---

## ✅ What Passed (4 checks)

1. **Example Builds** - hello-world compiles successfully ✅
2. **Required Sections** - All key docs have required sections ✅
3. **Config Schema** - Actual config files are valid ✅
4. **Version Consistency** - v0.7.0 consistent across files ✅

---

## Recommendations

### Immediate Actions
1. **Update verify_docs.py** - Improve regex to skip command examples
2. **Use `jsonc` tag** - For JSON blocks with comments/explanations

### Can Ignore
- File reference "issues" (they're example commands, not files)
- Broken links in planning docs (not user-facing)
- Missing language tags in planning docs (not user-facing)

### Future
- Add check exclusions for planning/internal docs
- Separate "documentation examples" from "actual configs"
- Add `--strict` mode vs `--relaxed` mode

---

## Action Plan

**Priority 1: Fix Tool (10 min)**
- Update regex to skip `cat`, `python3 -m json.tool`, etc.
- Add exclusions for non-user-facing docs
- Re-run verification

**Priority 2: Consider JSON Tag (5 min)**
- Decide: Use `jsonc` for commented examples?
- Or: Accept that docs show invalid JSON for clarity?
- Document decision

**Priority 3: Phase 2/3 Content**
- Create placeholder files if desired
- Or mark links as "Coming Soon"
- Or leave as-is (planning doc)

---

## Notes

- **Core docs (README, CONFIG_REFERENCE, FILTERS) are solid** ✅
- **hello-world example works** ✅
- **Actual config files are valid** ✅
- Issues found are mostly false positives or doc formatting choices
- Tool successfully validates what matters most

**Bottom line:** Phase 1 documentation is **production-ready**. Issues found are tool calibration, not doc problems.
