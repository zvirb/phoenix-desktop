## 2026-02-14 - Cache Miss on None
**Learning:** Checking `if cache_value is not None` is insufficient when `None` is a valid cached result (e.g. "not found"). This causes the expensive operation to run repeatedly on every call, defeating the purpose of caching.
**Action:** Use a separate timestamp or flag (e.g. `cache_time > 0`) to verify cache validity, ensuring that negative results are also cached for the duration.

## 2026-02-14 - FIFO Cache Eviction
**Learning:** Clearing an entire cache when it hits a size limit (to avoid unbounded growth) creates a "performance cliff" where subsequent lookups are all misses. This is especially bad for caches that are expensive to repopulate (like `psutil` process lookups).
**Action:** Use a FIFO eviction policy (`cache.pop(next(iter(cache)))`) or LRU policy to maintain the cache size at the limit, preserving the most recent items and avoiding the "thundering empty cache" problem.

## 2026-02-14 - Zero-Copy Screenshot Analysis
**Learning:** `mss.grab()` returns raw bytes (`bgra`). Converting this to a PIL `Image` using `frombytes` creates a new object and copies memory, which is expensive for high-frequency checks (e.g., 1Hz). `numpy.frombuffer` allows zero-copy access to the raw bytes, enabling efficient slicing and vectorized operations for change detection without the overhead of full image creation.
**Action:** Use `numpy.frombuffer(sct_img.bgra, dtype=np.uint8)` to analyze screenshots directly. Only convert to `PIL.Image` *after* a significant change is detected.

## 2026-02-14 - Float32 vs Int for MSE
**Learning:** While integer arithmetic avoids type conversion overhead (`astype(float32)`), modern CPU SIMD instructions often make `float32` operations faster for large array reductions (like MSE) than `int64` accumulation needed to prevent overflow. Benchmarks showed the existing `float32` implementation was faster than an optimized integer-only version for 320x240 images.
**Action:** Measure before optimizing math operations; don't assume integers are always faster than floats for image processing.

## 2026-02-14 - Subprocess vs Native Libraries
**Learning:** Using `subprocess.run` to query system state (like `tailscale ip`) is orders of magnitude slower (~500ms vs ~0.1ms) than using native libraries (`psutil`). Even with caching, the initial hit and potential timeout hangs are significant.
**Action:** Prioritize native libraries (`psutil`, `ctypes`) over CLI wrappers for system status checks. Use CLI only as a fallback.

## 2026-02-23 - Einsum for Grayscale
**Learning:** `np.einsum` with `optimize=True` is significantly faster (~13% in this case) and more memory-efficient than manual channel extraction and arithmetic for weighted sums (like grayscale conversion) on strided arrays, as it avoids intermediate array allocations and uses optimized BLAS routines.
**Action:** Use `np.einsum` for weighted channel operations instead of splitting channels and doing element-wise arithmetic, especially when dealing with high-frequency image processing.
