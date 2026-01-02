# Project TODOs & Known Issues

## v0.4.1 - Reliability Improvements
- [ ] **Fix Silent Failures in JSON Filter:** If the build command fails (exit code != 0) but the regex matches 0 errors, `gcc_json` should inject a "Synthetic Error" object containing the raw output or the `make` error message.
  *Current Behavior:* Returns `[]` on Makefile syntax errors.
  *Desired Behavior:* Returns `[{"type": "fatal", "message": "Makefile:2: *** missing separator"}]`