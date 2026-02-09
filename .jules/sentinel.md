# Sentinel's Security Journal

## 2024-05-22 - Debug Script Token Leakage
**Vulnerability:** Authentication tokens were being printed to stdout in root-level debug scripts (`check_token.py`, `debug_server.py`).
**Learning:** Utility scripts often bypass standard logging controls and can be a significant source of credential leakage if users are instructed to run them for support.
**Prevention:** Always review auxiliary scripts for sensitive data handling, and use centralized masking functions even in debug tools.

## 2026-02-04 - Insecure URL Validation Bypass
**Vulnerability:** `PHOENIX_API_URL` validation used `in` operator checks (`'localhost' in url`), allowing insecure HTTP connections to domains like `localhost.evil.com`.
**Learning:** String matching is insufficient for URL security validation; attacker-controlled substrings can bypass checks.
**Prevention:** Use `urllib.parse` to strictly validate scheme and exact hostname matches for security exceptions.
## 2024-05-23 - Sidecar Input Logging Leakage
**Vulnerability:** Raw user input containing potential PII or secrets was being logged to disk in the sidecar's `decompose_task` and input listener.
**Learning:** Background processes/sidecars often have separate logging configurations that miss centralized security policies.
**Prevention:** Ensure all entry points (like stdin listeners) validate and sanitize input immediately upon receipt before logging.

## 2026-02-06 - PII Leakage in Debug Logs
**Vulnerability:** The `api_client.send_heartbeat` method was logging the full `data` payload (including `window_title`) at DEBUG level. While typical configurations use INFO, centralized logging setups (like `PhoenixLogger`) often default to DEBUG for file outputs, risking persistent PII storage.
**Learning:** Debug logs are not safe zones; libraries must assume their debug output might be persisted in production environments.
**Prevention:** Always create a sanitized copy of data structures containing PII before passing them to any logging function, even `debug()`.

## 2026-06-02 - Plaintext Token Entry
**Vulnerability:** The device token was requested using `input()` in `update_token.py` and `phoenix/core/token_manager.py`, exposing the token in plaintext on the console during setup.
**Learning:** Standard input functions like `input()` are not secure for sensitive data entry as they echo characters to the screen and may be captured in shell history.
**Prevention:** Always use `getpass.getpass()` for sensitive inputs like passwords and tokens to mask the input.

## 2026-02-08 - Nested Dictionary and Return Value Leakage in Logs
**Vulnerability:** The `@logged_method` decorator and `PhoenixLogger` were logging function arguments (kwargs) and return values using `str()`, which exposed sensitive data nested within dictionaries (e.g., `{'user': {'token': '...'}}`). Simple keyword filtering on the top-level keys missed these nested secrets.
**Learning:** Shallow filtering of sensitive keys is insufficient for complex data structures; logging logic must be recursive to catch secrets buried deep in objects.
**Prevention:** Implement a recursive sanitization function with depth limits and cycle detection to redact sensitive keys at any level before logging.

## 2026-10-27 - Unsanitized API Response Logging
**Vulnerability:** The `APIClient` was logging the full JSON response body at DEBUG level using `logger.debug()`. This exposed sensitive data (like `access_token` and `Set-Cookie` headers returned by the server) in plain text in the log files.
**Learning:** Even when requests are sanitized, responses can contain new secrets (session tokens, cookies) that must also be redacted before logging. Standard `logging` does not automatically sanitize arguments.
**Prevention:** Always wrap API response objects in a sanitization function before passing them to any logger, especially when the response might contain authentication material.
