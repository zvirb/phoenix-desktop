## 2024-10-24 - Database Indexing on RequestQueue
**Learning:** `RequestQueue.peek()` was performing a full table scan and sort on every successful API call. Adding a composite index `(priority DESC, created_at ASC)` reduced query time from ~20ms to ~0.1ms (200x speedup) for 20k items.
**Action:** Always check `ORDER BY` clauses in frequently accessed SQLite tables and ensure appropriate indexes exist. Use `EXPLAIN QUERY PLAN` to verify.
