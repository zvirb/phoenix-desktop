# Sentinel's Security Journal

## 2024-05-22 - Debug Script Token Leakage
**Vulnerability:** Authentication tokens were being printed to stdout in root-level debug scripts (`check_token.py`, `debug_server.py`).
**Learning:** Utility scripts often bypass standard logging controls and can be a significant source of credential leakage if users are instructed to run them for support.
**Prevention:** Always review auxiliary scripts for sensitive data handling, and use centralized masking functions even in debug tools.

## 2024-05-23 - Sidecar Input Logging Leakage
**Vulnerability:** Raw user input containing potential PII or secrets was being logged to disk in the sidecar's `decompose_task` and input listener.
**Learning:** Background processes/sidecars often have separate logging configurations that miss centralized security policies.
**Prevention:** Ensure all entry points (like stdin listeners) validate and sanitize input immediately upon receipt before logging.
