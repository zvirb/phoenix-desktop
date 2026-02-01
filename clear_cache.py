"""Clear the pending uploads cache."""
from data_cache import DataCache

cache = DataCache()
stats = cache.get_stats()
print(f"Current cache: {stats['count']} items, {stats['size_bytes']} bytes")

if stats['count'] > 0:
    print("\nClearing cache...")
    if cache.clear_cache():
        print("✅ Cache cleared successfully!")
    else:
        print("❌ Failed to clear cache")
else:
    print("Cache is already empty.")
