class RedisScriptManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.script_cache = {}  # 缓存 {lua_script: sha1}

    def get_or_register_script(self, lua_script):
        """
        获取已注册的脚本 SHA1，如果未注册则注册
        """
        if lua_script not in self.script_cache:
            self.script_cache[lua_script] = self.redis_client.script_load(lua_script)
        return self.script_cache[lua_script]

    def execute_by_sha(self, sha1, keys, args):
        """
        通过 SHA1 调用 Lua 脚本
        """
        return self.redis_client.evalsha(sha1, len(keys), *keys, *args)
