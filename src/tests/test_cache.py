import time
import pytest
from app.utils.cache import get_cached_response, set_cached_response, clear_cache, CACHE_DIR

@pytest.fixture(autouse=True)
def run_around_tests():
    clear_cache()
    yield
    clear_cache()

def test_cache_hit_and_miss():
    engine = "google_flights"
    params = {"origin": "BLR", "destination": "DEL", "api_key": "somekey"}
    data = {"results": [{"airline": "IndiGo", "price": 5000}]}

    # Miss initially
    assert get_cached_response(engine, params) is None

    # Set response
    set_cached_response(engine, params, data)

    # Hit
    cached = get_cached_response(engine, params)
    assert cached == data

def test_cache_normalization():
    engine = "google_flights"
    
    # Swapped parameter ordering and different API keys
    params1 = {"origin": "BLR", "destination": "DEL", "api_key": "key1"}
    params2 = {"destination": "DEL", "origin": "BLR", "api_key": "key2"}
    
    data = {"results": [{"airline": "Air India"}]}
    
    set_cached_response(engine, params1, data)
    
    # Should hit even with swapped param order and different api_key
    cached = get_cached_response(engine, params2)
    assert cached == data

def test_cache_ttl_expiration():
    engine = "google_hotels"
    params = {"city": "Paris"}
    data = {"properties": []}
    
    set_cached_response(engine, params, data)
    
    # TTL = 0 should immediately expire
    assert get_cached_response(engine, params, ttl=0) is None
    
    # TTL = 10 should hit
    assert get_cached_response(engine, params, ttl=10) == data
