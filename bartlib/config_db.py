
import os
import logging
from typing import Optional
import redis


class ConfigDB:
    _log: logging.Logger = logging.getLogger("ConfigDB")
    _redis: redis.Redis
    _dict: dict

    def __init__(self):
        self._dict = {}

        self._redis = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")),
                                  db=int(os.getenv("REDIS_DB")), password=os.getenv("REDIS_PASSWORD"))

        try:
            self._redis.get("test")
        except (redis.ResponseError, redis.ConnectionError) as exc:
            self._log.error(f"Could not use redis: {str(exc)}")
            # disable it
            self._redis = None
    
    def set(self, key: str, val: any):
        # set in dict
        self._dict[key] = val
        # set in redis
        if self._redis is not None:
            self._redis.set(key, val)
    
    def get(self, key: str) -> Optional[any]:
        # get from redis
        if self._redis is not None:
            val = self._redis.get(key)
            if isinstance(val, bytes):
                # convert bytes to string
                val = val.decode("utf-8")
            # set to dict
            self._dict[key] = val
            self._log.info(f"Config key '{key}' read from redis: '{val}'")
            return val
        # get from dict
        return self._dict.get(key)
