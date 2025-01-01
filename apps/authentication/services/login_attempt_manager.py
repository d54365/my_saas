from django.core.cache import cache


class LoginAttemptManager:
    def __init__(self, identifier, max_attempts=5, lockout_time=7200, retry_time=3600):
        """
        初始化登录尝试管理器
        :param identifier: 用户标识符(用户名或手机号)
        :param max_attempts: 最大允许的失败次数
        :param lockout_time: 锁定时间, 单位为秒(默认2小时)
        :param retry_time: 重试窗口的时长，单位为秒(默认1小时)
        """
        self.identifier = identifier
        self.max_attempts = max_attempts
        self.lockout_time = lockout_time
        self.retry_time = retry_time
        self.cache_key_attempts = f"authentication:login_attempts:{self.identifier}"
        self.cache_key_locked = f"authentication:login_locked:{self.identifier}"

    def is_locked(self):
        """检查用户是否被锁定"""
        return cache.get(self.cache_key_locked) is not None

    def get_attempts(self):
        """获取当前失败次数"""
        return cache.get(self.cache_key_attempts, 0)

    def record_failed_attempts(self):
        """记录一次失败的登录尝试"""
        attempts = self.get_attempts()
        if attempts == 0:
            # 如果是第一次失败，设置失败次数为1并设置超时时间
            cache.set(self.cache_key_attempts, 1, timeout=self.retry_time)
        else:
            # 如果已经有失败次数，增加计数但不重置超时时间
            cache.incr(self.cache_key_attempts)

        if attempts >= self.max_attempts:
            self.lock_account()

    def lock_account(self):
        """锁定账户, 锁定时间到期后自动解锁"""
        cache.set(self.cache_key_locked, True, timeout=self.lockout_time)

        cache.delete(self.cache_key_attempts)

    def unlock_account(self):
        """手动解锁账户"""
        cache.delete(self.cache_key_locked)

    def reset_attempts(self):
        """重置登录尝试次数"""
        cache.delete(self.cache_key_attempts)
