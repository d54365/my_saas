class AuthConstants:
    SYSTEM_USER_DEVICE_SESSION_TEMPLATE = (
        "authentication:system_user:device_session:{user_id}:{device_id}"
    )
    SYSTEM_USER_ALL_SESSIONS_TEMPLATE = (
        "authentication:system_user:all_session:{user_id}"
    )
    SYSTEM_USER_ACTIVE = "accounts:system_user:active"  # nosec
    ACCESS_TOKEN_BLACKLIST = "authentication:jwt:access:blacklist"  # nosec
    REFRESH_TOKEN_BLACKLIST = "authentication:jwt:refresh:blacklist"  # nosec
