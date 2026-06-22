import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

CACHE_TTL_SECONDS = 86400

def get_cached_url(short_code:str):
    return redis_client.get(f"url:{short_code}")

def cache_url(short_code:str, long_url:str, ttl:int = CACHE_TTL_SECONDS):
    return redis_client.setex(f"url:{short_code}", ttl, long_url)

def invalidate_url(short_code:str):
    return redis_client.delete(f"url:{short_code}")

