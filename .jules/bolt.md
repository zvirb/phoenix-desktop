## 2026-02-14 - Cache Miss on None
**Learning:** Checking `if cache_value is not None` is insufficient when `None` is a valid cached result (e.g. "not found"). This causes the expensive operation to run repeatedly on every call, defeating the purpose of caching.
**Action:** Use a separate timestamp or flag (e.g. `cache_time > 0`) to verify cache validity, ensuring that negative results are also cached for the duration.

## 2026-02-14 - FIFO Cache Eviction
**Learning:** Clearing an entire cache when it hits a size limit (to avoid unbounded growth) creates a "performance cliff" where subsequent lookups are all misses. This is especially bad for caches that are expensive to repopulate (like `psutil` process lookups).
**Action:** Use a FIFO eviction policy (`cache.pop(next(iter(cache)))`) or LRU policy to maintain the cache size at the limit, preserving the most recent items and avoiding the "thundering empty cache" problem.
