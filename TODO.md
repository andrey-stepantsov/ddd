# Project TODOs & Known Issues

## v0.4.1 - Reliability Improvements
- [ ] **Fix Silent Failures in JSON Filter:** If the build command fails (exit code != 0) but the regex matches 0 errors, `gcc_json` should inject a "Synthetic Error" object containing the raw output or the `make` error message.

## v0.5.0 - Observability & Metrics
- [ ] **Build Summary Stats:** Append a footer to `build.log` with processing metrics.
  *Metrics:*
    - Raw Log Size (KB / Lines)
    - Filtered Output Size (KB / Lines)
    - Duration (Seconds)
    - Compression Ratio (Raw / Filtered)
    - Token Estimate (Approx. 4 chars per token)
