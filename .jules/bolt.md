## 2026-02-14 - Cache Miss on None
**Learning:** Checking `if cache_value is not None` is insufficient when `None` is a valid cached result (e.g. "not found"). This causes the expensive operation to run repeatedly on every call, defeating the purpose of caching.
**Action:** Use a separate timestamp or flag (e.g. `cache_time > 0`) to verify cache validity, ensuring that negative results are also cached for the duration.
