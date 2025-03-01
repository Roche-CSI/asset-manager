from typing import Dict, Optional, Any, List
import time
from datetime import datetime, timedelta
import numpy as np
from threading import Lock
from functools import lru_cache
from collections import OrderedDict
import weakref


class SimpleCache:
    """Simple dictionary-based cache with TTL"""

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = Lock()

    def set(self, key: str, value: Any, ttl: int = 3600):
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                self.cache.popitem(last=False)

            expiry = datetime.now() + timedelta(seconds=ttl)
            self.cache[key] = (value, expiry)

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None

            value, expiry = self.cache[key]
            if datetime.now() > expiry:
                del self.cache[key]
                return None

            return value

    def clear(self):
        with self.lock:
            self.cache.clear()


class LRUCache:
    """LRU Cache implementation using OrderedDict"""

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.max_size:
                # Remove least recently used item
                self.cache.popitem(last=False)


class WeakRefCache:
    """Cache using weak references - good for large objects"""

    def __init__(self):
        self.cache = weakref.WeakValueDictionary()
        self.lock = Lock()

    def set(self, key: str, value: Any):
        with self.lock:
            self.cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            return self.cache.get(key)


class VectorSearchCache:
    """Specialized cache for vector search operations"""

    def __init__(self,
                 embedding_cache_size: int = 1000,
                 result_cache_size: int = 100):
        # Cache for embeddings
        self.embedding_cache = LRUCache(embedding_cache_size)
        # Cache for search results
        self.result_cache = SimpleCache(result_cache_size)

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        return self.embedding_cache.get(text)

    def set_embedding(self, text: str, embedding: np.ndarray):
        self.embedding_cache.set(text, embedding)

    def get_search_results(self, query: str) -> Optional[List[Dict]]:
        return self.result_cache.get(query)

    def set_search_results(self,
                           query: str,
                           results: List[Dict],
                           ttl: int = 3600):
        self.result_cache.set(query, results, ttl)


def demonstrate_caching():
    """Demonstrate different caching strategies"""

    # 1. Simple Cache
    print("\nTesting Simple Cache:")
    simple_cache = SimpleCache(max_size=2)

    # Set values
    simple_cache.set("key1", "value1", ttl=2)
    simple_cache.set("key2", "value2", ttl=2)

    # Get values
    print(f"Key1: {simple_cache.get('key1')}")
    print(f"Key2: {simple_cache.get('key2')}")

    # Test TTL
    time.sleep(3)
    print(f"After TTL - Key1: {simple_cache.get('key1')}")

    # 2. LRU Cache
    print("\nTesting LRU Cache:")
    lru_cache = LRUCache(max_size=2)

    # Set values
    lru_cache.set("key1", "value1")
    lru_cache.set("key2", "value2")
    lru_cache.set("key3", "value3")  # Should evict key1

    # Check values
    print(f"Key1 (should be None): {lru_cache.get('key1')}")
    print(f"Key2: {lru_cache.get('key2')}")
    print(f"Key3: {lru_cache.get('key3')}")

    # 3. Vector Search Cache
    print("\nTesting Vector Search Cache:")
    vector_cache = VectorSearchCache()

    # Test with embeddings
    embedding = np.array([0.1, 0.2, 0.3])
    vector_cache.set_embedding("test query", embedding)

    cached_embedding = vector_cache.get_embedding("test query")
    print(f"Retrieved embedding: {cached_embedding}")

    # Test with search results
    results = [{"id": 1, "score": 0.9}, {"id": 2, "score": 0.8}]
    vector_cache.set_search_results("test query", results)

    cached_results = vector_cache.get_search_results("test query")
    print(f"Retrieved results: {cached_results}")


if __name__ == "__main__":
    demonstrate_caching()