import os


def try_parse_int(value: str):
    try:
        return int(value)
    except Exception:
        return None


# Configuration for the Store API
STORE_API_HOST = os.environ.get("STORE_API_HOST") or "localhost"
STORE_API_PORT = try_parse_int(os.environ.get("STORE_API_PORT")) or 8000
STORE_API_BASE_URL = f"http://{STORE_API_HOST}:{STORE_API_PORT}"

# Configure for Redis
REDIS_HOST = os.environ.get("REDIS_HOST") or "localhost"
REDIS_PORT = try_parse_int(os.environ.get("REDIS_PORT")) or 6379

# Configure for hub logic
BATCH_SIZE = try_parse_int(os.environ.get("BATCH_SIZE")) or 20

# Configure for logging
LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"