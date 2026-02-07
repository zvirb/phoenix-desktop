## 2024-10-24 - Database Indexing on RequestQueue
**Learning:** `RequestQueue.peek()` was performing a full table scan and sort on every successful API call. Adding a composite index `(priority DESC, created_at ASC)` reduced query time from ~20ms to ~0.1ms (200x speedup) for 20k items.
**Action:** Always check `ORDER BY` clauses in frequently accessed SQLite tables and ensure appropriate indexes exist. Use `EXPLAIN QUERY PLAN` to verify.

## 2024-10-26 - Caching Active Window Process Lookup
**Learning:** `WindowDetector` was creating a new `psutil.Process` object and resolving the process name every second (or more often) for the active window. Caching the `app_name` keyed by the window handle (`hwnd`) eliminates these repeated system calls when the user stays in the same window.
**Action:** When polling system state (like active window), identify stable identifiers (like `hwnd`) and cache expensive property lookups until the identifier changes.

## 2026-02-07 - PID Caching for Window Detection
**Learning:** Caching `app_name` only by `hwnd` causes redundant `psutil` lookups when switching between windows of the same application (same PID) or repeatedly switching between cached apps. Adding a persistent `pid -> app_name` cache significantly reduces system calls and `psutil.Process` instantiations.
**Action:** Cache expensive lookups at the most stable entity level (PID) rather than the most volatile (HWND) when possible.
