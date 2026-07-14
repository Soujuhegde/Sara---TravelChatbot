import os
import json
import hashlib
import time
from typing import Dict, Any, Optional

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.cache/serpapi"))
DEFAULT_TTL = 3600  # Default 1 hour TTL for flights/hotels cache

def _get_cache_path(engine: str, params: Dict[str, Any]) -> str:
    # Filter out api_key and other irrelevant parameters from the cache key
    ignored_keys = {"api_key", "timestamp", "session_id", "task_id", "hl", "gl"}
    filtered_params = {k: v for k, v in params.items() if k not in ignored_keys}
    
    # Sort keys to ensure stable hashing
    serialized = json.dumps(filtered_params, sort_keys=True)
    param_hash = hashlib.md5(serialized.encode("utf-8")).hexdigest()
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, f"{engine}_{param_hash}.json")

def get_cached_response(engine: str, params: Dict[str, Any], ttl: int = DEFAULT_TTL) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached SerpAPI response if it exists and has not expired.
    """
    cache_file = _get_cache_path(engine, params)
    if os.path.exists(cache_file):
        try:
            # Check modification time to enforce TTL
            mtime = os.path.getmtime(cache_file)
            if time.time() - mtime < ttl:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(f"[CACHE HIT] Found valid cache for engine={engine}")
                return data
            else:
                print(f"[CACHE EXPIRED] Cache file expired for engine={engine}")
        except Exception as e:
            print(f"Error reading cache file {cache_file}: {e}")
    return None

def set_cached_response(engine: str, params: Dict[str, Any], data: Dict[str, Any]):
    """
    Save the SerpAPI response to the disk cache.
    """
    cache_file = _get_cache_path(engine, params)
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[CACHE SAVE] Saved response to cache file {cache_file}")
    except Exception as e:
        print(f"Error saving to cache file {cache_file}: {e}")

def clear_cache():
    """
    Clear all cached files.
    """
    if os.path.exists(CACHE_DIR):
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error clearing cache file {file_path}: {e}")
