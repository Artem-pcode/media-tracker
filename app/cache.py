import redis.asyncio as redis
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def invalidate_titles_cache(list_content_type: List[str]):
    keys_to_delete = ["titles:all"]
    keys_to_delete.extend(list_content_type)
    keys_to_delete = list(set(keys_to_delete))
    if len(keys_to_delete) > 0:
        print("deleted")
        await redis_client.delete(*keys_to_delete)