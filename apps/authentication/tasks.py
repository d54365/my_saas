from datetime import datetime, timedelta

from authentication.constants import AuthConstants
from celery import shared_task
from common.cache.redis import script_manager
from django.core.cache import cache
from django.utils import timezone


@shared_task(name="clean_expiration_access_token")
def clean_expiration_access_token(*args, **kwargs):
    return cache.zremrangebyscore(
        AuthConstants.ACCESS_TOKEN_BLACKLIST,
        0,
        timezone.now().timestamp(),
    )


@shared_task(name="clean_expiration_refresh_token")
def clean_expiration_refresh_token(*args, **kwargs):
    return cache.zremrangebyscore(
        AuthConstants.REFRESH_TOKEN_BLACKLIST,
        0,
        timezone.now().timestamp(),
    )


@shared_task(name="clean_expired_sessions")
def clean_expired_sessions(*args, **kwargs):
    lua_script = """
    -- KEYS[1]: 活跃用户集合的键名
    -- ARGV[1]: 当前时间戳

    local active_users_set = KEYS[1]
    local current_timestamp = tonumber(ARGV[1])

    -- 获取所有活跃用户
    local active_users = redis.call("SMEMBERS", active_users_set)

    for _, user_id in ipairs(active_users) do
        -- 获取用户的所有设备会话集合键名
        local user_sessions_key = string.format("system_user_sessions:%s", user_id)
        local device_ids = redis.call("SMEMBERS", user_sessions_key)

        for _, device_id in ipairs(device_ids) do
            -- 获取设备的会话键名
            local session_key = string.format("system_user_session:%s:%s", user_id, device_id)
            local session_data = redis.call("GET", session_key)

            if session_data then
                local session = cjson.decode(session_data)
                local refresh_expired_time = tonumber(session["refresh_expired_time"] or 0)
                local access_expired_time = tonumber(session["access_expired_time"] or 0)

                -- 如果会话已过期，删除会话数据
                if (refresh_expired_time <= current_timestamp) and (access_expired_time <= current_timestamp) then
                    redis.call("DEL", session_key)
                    redis.call("SREM", user_sessions_key, device_id)
                end
            end
        end

        -- 如果用户已无活跃设备，移除用户
        if redis.call("SCARD", user_sessions_key) == 0 then
            redis.call("SREM", active_users_set, user_id)
        end
    end

    return "Expired sessions cleaned."
    """

    sha1 = script_manager.get_or_register_script(lua_script)

    # 执行脚本
    current_timestamp = int(datetime.utcnow().timestamp())
    result = script_manager.execute_by_sha(
        sha1=sha1, keys=[AuthConstants.SYSTEM_USER_ACTIVE], args=[current_timestamp]
    )
    return result


@shared_task(name="update_user_last_active")
def update_user_last_active(device_session_key, *args, **kwargs):
    session_data = cache.get(device_session_key)
    if session_data:
        now = timezone.now()

        session_data["last_active_at"] = now

        # 动态计算剩余 TTL
        refresh_expired_at = session_data["login_at"] + timedelta(
            seconds=session_data["refresh_expired_second"],
        )
        remaining_ttl = (refresh_expired_at - now).total_seconds()

        if remaining_ttl > 0:
            cache.set(device_session_key, session_data, timeout=int(remaining_ttl))
