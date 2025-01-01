import copy
from typing import Any, List, Optional, Union

from django_redis.cache import RedisCache, omit_exception


class ExtendedRedisCache(RedisCache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _make_key(self, key: str):
        return self.make_key(key, version=self.version)

    def _encode_value(self, value):
        if value is None:
            return value
        return self.client.encode(value)

    def _decode_value(self, value):
        if value is None:
            return value
        return self.client.decode(value)

    @omit_exception
    def hset(
        self,
        name: str,
        key: Optional[str] = None,
        value: Optional[str] = None,
        mapping: Optional[dict] = None,
    ):
        full_name = self._make_key(name)
        client = self.client.get_client(write=True)
        if mapping:
            encoded_mapping = copy.deepcopy(mapping)
            for k, v in encoded_mapping.items():
                encoded_mapping[k] = self._encode_value(v)
            return client.hset(full_name, mapping=encoded_mapping)
        elif key and value:
            encoded_value = self._encode_value(value)
            return client.hset(full_name, key, encoded_value)
        raise ValueError("Either `key` and `value` or `mapping` must be provided")

    @omit_exception
    def hget(self, name: str, key: str):
        raw_value = self.client.get_client(write=False).hget(self._make_key(name), key)
        return self._decode_value(raw_value) if raw_value else None

    @omit_exception
    def hexists(self, name: str, key: str):
        return self.client.get_client(write=False).hexists(self._make_key(name), key)

    @omit_exception
    def hdel(self, name: str, *keys: str):
        return self.client.get_client(write=True).hdel(self._make_key(name), *keys)

    @omit_exception
    def hmget(self, name: str, keys: List[str]):
        raw_values = self.client.get_client(write=False).hmget(
            self._make_key(name), *keys
        )
        return [self._decode_value(value) for value in raw_values]

    @omit_exception
    def hgetall(self, name: str):
        raw_values = self.client.get_client(write=False).hgetall(self._make_key(name))
        return {k.decode("utf-8"): self._decode_value(v) for k, v in raw_values.items()}

    @omit_exception
    def lpush(self, name: str, *values):
        full_name = self._make_key(name)
        encoded_values = [self._encode_value(value) for value in values]
        return self.client.get_client(write=True).lpush(full_name, *encoded_values)

    @omit_exception
    def rpush(self, name: str, *values):
        full_name = self._make_key(name)
        encoded_values = [self._encode_value(value) for value in values]
        return self.client.get_client(write=True).rpush(full_name, *encoded_values)

    @omit_exception
    def lpop(self, name: str):
        return self._decode_value(
            self.client.get_client(write=True).lpop(self._make_key(name))
        )

    @omit_exception
    def rpop(self, name: str):
        return self._decode_value(
            self.client.get_client(write=True).rpop(self._make_key(name))
        )

    @omit_exception
    def llen(self, name: str):
        return self.client.get_client(write=False).llen(self._make_key(name))

    @omit_exception
    def lrange(self, name: str, start: int, end: int):
        raw_values = self.client.get_client(write=False).lrange(
            self._make_key(name), start, end
        )
        return [self._decode_value(value) for value in raw_values]

    @omit_exception
    def lset(self, name: str, index: int, value):
        return self.client.get_client(write=True).lset(
            self._make_key(name), index, self._encode_value(value)
        )

    @omit_exception
    def linsert(self, name: str, where: str, refvalue, value):
        return self.client.get_client(write=True).linsert(
            self._make_key(name), where, refvalue, self._encode_value(value)
        )

    @omit_exception
    def ltrim(self, name: str, start: int, end: int):
        return self.client.get_client(write=True).ltrim(
            self._make_key(name), start, end
        )

    @omit_exception
    def blpop(self, keys: List[str], timeout: int = 0):
        full_keys = [self._make_key(key) for key in keys]
        return self.client.get_client(write=True).blpop(full_keys, timeout)

    @omit_exception
    def brpop(self, keys: List[str], timeout: int = 0):
        full_keys = [self._make_key(key) for key in keys]
        return self.client.get_client(write=True).brpop(full_keys, timeout)

    @omit_exception
    def brpoplpush(self, src: str, dst: str, timeout: int = 0):
        return self.client.get_client(write=True).brpoplpush(
            self._make_key(src), self._make_key(dst), timeout
        )

    # Set
    @omit_exception
    def sadd(self, name: str, *values):
        return self.client.get_client(write=True).sadd(
            self._make_key(name), *[self._encode_value(value) for value in values]
        )

    @omit_exception
    def srem(self, name: str, *values):
        return self.client.get_client(write=True).srem(
            self._make_key(name), *[self._encode_value(value) for value in values]
        )

    @omit_exception
    def smove(self, src: str, dst: str, value):
        return self.client.get_client(write=True).smove(
            self._make_key(src), self._make_key(dst), self._encode_value(value)
        )

    @omit_exception
    def smembers(self, name: str):
        raw_values = self.client.get_client(write=False).smembers(self._make_key(name))
        return {self._decode_value(value) for value in raw_values}

    @omit_exception
    def scard(self, name: str):
        return self.client.get_client(write=False).scard(self._make_key(name))

    @omit_exception
    def sismember(self, name: str, value):
        return self.client.get_client(write=False).sismember(
            self._make_key(name), self._encode_value(value)
        )

    @omit_exception
    def srandmember(self, name: str, number: Optional[int] = None):
        raw_values = self.client.get_client(write=False).srandmember(
            self._make_key(name), number
        )
        if isinstance(raw_values, list):
            return [self._decode_value(value) for value in raw_values]
        return self._decode_value(raw_values)

    @omit_exception
    def spop(self, name: str):
        return self._decode_value(
            self.client.get_client(write=True).spop(self._make_key(name))
        )

    @omit_exception
    def sinterstore(self, dest: str, keys: List[str]):
        full_keys = [self._make_key(key) for key in keys]
        return self.client.get_client(write=True).sinterstore(
            self._make_key(dest), *full_keys
        )

    @omit_exception
    def sunionstore(self, dest: str, keys: List[str]):
        full_keys = [self._make_key(key) for key in keys]
        return self.client.get_client(write=True).sunionstore(
            self._make_key(dest), *full_keys
        )

    @omit_exception
    def sdiffstore(self, dest: str, keys: List[str]):
        full_keys = [self._make_key(key) for key in keys]
        return self.client.get_client(write=True).sdiffstore(
            self._make_key(dest), *full_keys
        )

    @omit_exception
    def zadd(self, name: str, mapping: dict):
        full_name = self._make_key(name)
        encoded_mapping = {self._encode_value(k): v for k, v in mapping.items()}
        return self.client.get_client(write=True).zadd(
            full_name, mapping=encoded_mapping
        )

    @omit_exception
    def zrem(self, name: str, *values):
        return self.client.get_client(write=True).zrem(
            self._make_key(name), *[self._encode_value(value) for value in values]
        )

    @omit_exception
    def zscore(self, name: str, value):
        return self.client.get_client(write=False).zscore(
            self._make_key(name), self._encode_value(value)
        )

    @omit_exception
    def zincrby(self, name: str, amount: float, value):
        return self.client.get_client(write=True).zincrby(
            self._make_key(name), amount, self._encode_value(value)
        )

    @omit_exception
    def zrank(self, name: str, value):
        return self.client.get_client(write=False).zrank(
            self._make_key(name), self._encode_value(value)
        )

    @omit_exception
    def zrevrank(self, name: str, value):
        return self.client.get_client(write=False).zrevrank(
            self._make_key(name), self._encode_value(value)
        )

    @omit_exception
    def zrange(
        self,
        name: str,
        start: int,
        end: int,
        desc: bool = False,
        withscores: bool = False,
    ):
        raw_values = self.client.get_client(write=False).zrange(
            self._make_key(name), start, end, desc=desc, withscores=withscores
        )
        if withscores:
            return [(self._decode_value(value[0]), value[1]) for value in raw_values]
        return [self._decode_value(value) for value in raw_values]

    @omit_exception
    def zrevrange(self, name: str, start: int, end: int, withscores: bool = False):
        raw_values = self.client.get_client(write=False).zrevrange(
            self._make_key(name), start, end, withscores=withscores
        )
        if withscores:
            return [(self._decode_value(value[0]), value[1]) for value in raw_values]
        return [self._decode_value(value) for value in raw_values]

    @omit_exception
    def zrangebyscore(
        self,
        name: str,
        min: Union[int, float],
        max: Union[int, float],
        withscores: bool = False,
    ):
        raw_values = self.client.get_client(write=False).zrangebyscore(
            self._make_key(name), min, max, withscores=withscores
        )
        if withscores:
            return [(self._decode_value(value[0]), value[1]) for value in raw_values]
        return [self._decode_value(value) for value in raw_values]

    @omit_exception
    def zrevrangebyscore(
        self,
        name: str,
        max: Union[int, float],
        min: Union[int, float],
        withscores: bool = False,
    ):
        raw_values = self.client.get_client(write=False).zrevrangebyscore(
            self._make_key(name), max, min, withscores=withscores
        )
        if withscores:
            return [(self._decode_value(value[0]), value[1]) for value in raw_values]
        return [self._decode_value(value) for value in raw_values]

    @omit_exception
    def zcount(self, name: str, min: Union[int, float], max: Union[int, float]):
        return self.client.get_client(write=False).zcount(
            self._make_key(name), min, max
        )

    @omit_exception
    def zremrangebyrank(self, name: str, start: int, end: int):
        return self.client.get_client(write=True).zremrangebyrank(
            self._make_key(name), start, end
        )

    @omit_exception
    def zremrangebyscore(
        self, name: str, min: Union[int, float], max: Union[int, float]
    ):
        return self.client.get_client(write=True).zremrangebyscore(
            self._make_key(name), min, max
        )

    def pipeline(self):
        # 注意: pipeline 时, 操作的 key 都需要 make_key, 否则 delete 或其他操作可能就匹配不上对应的 key
        return self.client.get_client(write=True).pipeline()

    def lock(
        self,
        name: str,
        timeout: Optional[float] = None,
        sleep: float = 0.1,
        blocking: bool = True,
        blocking_timeout: Optional[float] = None,
        lock_class: Union[None, Any] = None,
        thread_local: bool = True,
    ):
        full_name = self._make_key(name)
        client = self.client.get_client(write=True)
        return client.lock(
            full_name,
            timeout=timeout,
            sleep=sleep,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
            lock_class=lock_class,
            thread_local=thread_local,
        )

    def script_load(self, script: str):
        client = self.client.get_client(write=True)
        return client.script_load(script)

    def evalsha(self, sha: str, numkeys: int, *keys_and_args: str):
        # 注意: 操作的 key 是否需要 make_key, 否则可能就匹配不上对应的 key
        client = self.client.get_client(write=True)
        return client.evalsha(sha, numkeys, *keys_and_args)

    def eval(self, script: str, numkeys: int, *keys_and_args: str):
        # 注意: 操作的 key 是否需要 make_key, 否则可能就匹配不上对应的 key
        client = self.client.get_client(write=True)
        return client.eval(script, numkeys, *keys_and_args)

    @omit_exception
    def exists(self, name: str):
        client = self.client.get_client(write=True)
        return client.exists(name)
