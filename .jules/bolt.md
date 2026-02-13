## 2024-10-24 - Database Indexing on RequestQueue
**Learning:** `RequestQueue.peek()` was performing a full table scan and sort on every successful API call. Adding a composite index `(priority DESC, created_at ASC)` reduced query time from ~20ms to ~0.1ms (200x speedup) for 20k items.
**Action:** Always check `ORDER BY` clauses in frequently accessed SQLite tables and ensure appropriate indexes exist. Use `EXPLAIN QUERY PLAN` to verify.

## 2024-10-26 - Caching Active Window Process Lookup
**Learning:** `WindowDetector` was creating a new `psutil.Process` object and resolving the process name every second (or more often) for the active window. Caching the `app_name` keyed by the window handle (`hwnd`) eliminates these repeated system calls when the user stays in the same window.
**Action:** When polling system state (like active window), identify stable identifiers (like `hwnd`) and cache expensive property lookups until the identifier changes.

## 2026-02-06 - Optimized Activity Detection MSE Calculation
**Learning:** `ActivityDetector._calculate_similarity_mse` was performing unnecessary casting to `float64` (`.astype("float")`) which involved expensive memory copying. Since input images are already `float32`, performing arithmetic directly in `float32` yields a ~2x speedup for this frequent operation. Using `.astype(np.float32, copy=False)` ensures safety for non-float inputs while preserving zero-copy performance for float inputs.
**Action:** When working with NumPy arrays, use `.astype(dtype, copy=False)` to ensure correct types without incurring copy costs when the type already matches.
## 2026-02-07 - PID Caching for Window Detection
**Learning:** Caching `app_name` only by `hwnd` causes redundant `psutil` lookups when switching between windows of the same application (same PID) or repeatedly switching between cached apps. Adding a persistent `pid -> app_name` cache significantly reduces system calls and `psutil.Process` instantiations.
**Action:** Cache expensive lookups at the most stable entity level (PID) rather than the most volatile (HWND) when possible.

## 2026-02-08 - Optimized Gaming Process Detection
**Learning:** `GamingDetector.is_gaming` was iterating over all system processes (`psutil.process_iter`) every second, taking 50-200ms and consuming significant CPU. By passing the already-known active window process name to the detector, we can perform an O(1) hash lookup against the gaming blacklist, eliminating the O(N) system call overhead for 99% of cases.
**Action:** When checking for specific process states, prioritize checking the active context (foreground window) before falling back to full system scans.

## 2026-02-08 - Reduced ctypes Overhead in WindowDetector
**Learning:** `WindowDetector.get_idle_time` was defining a `ctypes.Structure` class and importing `ctypes` inside the function, which is called every second. This added ~50µs overhead per call and created unnecessary Python objects. Moving definitions to the module level eliminated this overhead.
**Action:** Avoid defining classes or importing modules inside frequently called loops. Pre-allocate structures and library handles at module level or `__init__`.

## 2026-02-09 - Defer Expensive Image Operations
**Learning:** `process_screenshot` was capturing, resizing (1920->1024), and JPEG compressing *every* captured frame before checking for significant changes. By checking for changes on the raw captured image *first* (using a fast resize-check), we avoid the expensive high-quality resize and JPEG compression for the 90%+ of cases where the screen hasn't changed.
**Action:** In processing pipelines, perform cheap "gating" checks (like diffs) as early as possible on raw data before performing expensive transformations (resize, encode, upload).

## 2026-02-15 - Fast Resampling for Activity Detection
**Learning:** `ActivityDetector.has_significant_change` was using `Image.Resampling.BILINEAR` to downscale screenshots (1920x1080 -> 320x240) for change detection. Benchmarking revealed `NEAREST` resampling is ~38x faster (0.3ms vs 12ms). Since the goal is detecting *significant* changes, the aliasing from `NEAREST` is an acceptable trade-off for the massive speedup.
**Action:** When downscaling images for change detection (not display), prefer `NEAREST` resampling to save CPU cycles.

## 2026-02-16 - Direct Image Conversion for Activity Detection
**Learning:** `ImageOps.grayscale` adds overhead by checking image modes and handling pallets. For RGB images, `image.convert('L')` is ~40% faster (measured 0.030s vs 0.050s per 100 iters) as it directly invokes the C-optimized conversion path.
**Action:** Use `.convert()` methods directly when source and target modes are known, avoiding wrapper overhead in tight loops.

## 2026-03-03 - Gaming Process Blacklist O(1) Lookup
**Learning:** `GamingDetector` was using a `List` for checking if a process is a game, which is O(N) where N is the number of blacklisted games. Inside the "slow path" (iterating all system processes), this check runs for every process (P), making it O(P*N). By converting the blacklist to a `Set`, the check becomes O(1), making the loop O(P). Benchmarking showed a ~60x speedup for 1000 gaming processes.
**Action:** Always use `set` for membership testing when iterating over collections, especially inside loops.
