from typing import Union
import redis
from fastapi import FastAPI
import pickle
import json


class RedisCache():
    def __init__(self, host: str, port: str):
        self.host = host
        self.port = port
        self.cache = None
    
    def init_app(self, app: FastAPI):
        @app.on_event("startup")
        def startup():
            try:
                self.cache = redis.Redis(host=self.host, port=self.port, db=0)
            except Exception as e:
                print(f"Failed to connect to redis: {e}")
                raise
        @app.on_event("shutdown")
        def shutdown():
            self.cache.connection_pool.disconnect()
    
    def init(self):
        try:
            self.cache = redis.Redis(host=self.host, port=self.port, db=0)
        except Exception as e:
            print(f"Failed to connect to redis: {e}")
            raise
    
    def shutdown(self):
        self.cache.connection_pool.disconnect()
    
    def set_cache(self, key: str, value: str, ex: int=86_400*3) -> bool: # 86,400 -> 24시간
        if self.cache is not None:
            value = pickle.dumps(value)
            res = self.cache.set(key, value, ex)
            return res
        else:
            print('redis connection is not available.')
            return False
    
    def get_cache(self, key: str) -> Union[dict, None]:
        if self.cache is not None:
            value = self.cache.get(key)
            if type(value) == bytes:
                value = pickle.loads(value)
            if type(value) == str:
                try:
                    value = json.loads(value)
                except:
                    pass
            else:
                pass
            return value
        else:
            print('redis connection is not available.')
            return None
    
    def delete_cache(self, key: str) -> Union[bool, None]:
        if self.cache is not None:
            if self.get_cache(key) is not None:
                res = self.cache.delete(key)
                if res:
                    return res
                else:
                    print('cache_key:', key)
                    print('Failed to delete cache.')
                    return None
            else:
                print('cache_key:', key)
                print('No cache information found.')
                None
        else:
            print('redis connection is not available.')
            return None
    
    def delete_cache_by_pattern(self, pattern: str, prefix: bool = True, suffix: bool = False):
        if prefix:
            pattern = f"{pattern}*"
        if suffix:
            pattern = f"*{pattern}"
        if self.cache is not None:
            keys_to_delete = self.cache.keys(pattern)
            if keys_to_delete:
                print(keys_to_delete)
                self.cache.delete(*keys_to_delete)
        else:
            print('redis connection is not available.')
            return None