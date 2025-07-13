#!/usr/bin/env python3
"""
Redis config file
"""


import redis
import uuid
from typing import Union, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''
    Decorator that counts how many times a method is called
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Wrapper that increments the count and calls'''
        key = method.__qualname__
        self._redis.incr(key)

        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    '''
    Class for redis cache
    '''

    def __init__(self):
        '''
        Initializes the Redis client and flushes the current database.
        '''
        self._redis = redis.Redis(
            host='localhost', port=6379, decode_responses=False)
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str | int | float | bytes]) -> str:
        """
        Stores the given data in Redis with a generated UUID key.

        Args:
            data (str | bytes | int | float): The data to store.

        Returns:
            str: The generated UUID key under which the data is stored.
        """

        uuid_value = str(uuid.uuid4())
        self._redis.set(uuid_value, data)

        return uuid_value

    def get(
            self, key: str, fn: Optional[Callable] = None
    ) -> Optional[Union[str, int, bytes]]:
        """
        Retrieve data from redis
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """
        Retrieves string data from redis
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> str:
        """
        Retrieves int from redis
        """
        return self.get(key, fn=int)
