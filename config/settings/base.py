import os.path
import sys
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(f"{BASE_DIR}/.env")

DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

LOCAL_APPS = [
    "accounts",
    "authentication",
    "tasks",
    "log",
    "tenant",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "django_celery_beat",
]
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    "common.middlewares.client_request_log.ClientRequestLogMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "common.middlewares.update_last_active.UpdateLastActiveMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": env.str("DB_ENGINE", "dj_db_conn_pool.backends.mysql"),
        "NAME": env("DB_NAME"),
        "HOST": env("DB_HOST"),
        "PORT": env.int("DB_PORT"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "POOL_OPTIONS": {
            "POOL_SIZE": env.int("DB_POOL_SIZE", 10),
            "MAX_OVERFLOW": env.int("DB_POOL_MAX_OVERFLOW", 10),
            "RECYCLE": env.int("DB_POOL_RECYCLE", 1800),
            "TIMEOUT": env.int("DB_POOL_TIMEOUT", 30),
            "RETRY_ATTEMPTS": env.int("DB_POOL_RETRY_ATTEMPTS", 3),
            "RETRY_DELAY": env.int("DB_POOL_RETRY_DELAY", 5),
        },
    },
    "clickhouse": {
        "ENGINE": "clickhouse_backend.backend",
        "NAME": env("CLICKHOUSE_NAME"),
        "HOST": env("CLICKHOUSE_HOST"),
        "USER": env("CLICKHOUSE_USER"),
        "PASSWORD": env("CLICKHOUSE_PASSWORD"),
    },
}

DATABASE_ROUTERS = [
    "common.db.routers.ClickHouseRouter",
]

LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "Simplified Chinese"),
)

LANGUAGE_CODE = "en-us"

LOCALE_PATHS = (f"{BASE_DIR}/locales",)

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DATETIME_INPUT_FORMATS": ("%Y-%m-%d %H:%M:%S",),
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M",
    "EXCEPTION_HANDLER": "common.exceptions.exception_handler",
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 1048576000

AUTH_USER_MODEL = "accounts.SystemUser"

CACHES = {
    "default": {
        "BACKEND": "common.cache.redis.cache_backends.ExtendedRedisCache",
        "LOCATION": env.str("REDIS_DSN"),
        "OPTIONS": {
            "SOCKET_CONNECT_TIMEOUT": env.int("REDIS_SOCKET_CONNECT_TIMEOUT", 5),
            "SOCKET_TIMEOUT": env.int("REDIS_SOCKET_TIMEOUT", 5),
            "COMPRESSOR": "common.cache.compressors.Lz4Compressor",
            "SERIALIZER": "common.cache.serializers.PickleSerializer",
            "PICKLE_VERSION": -1,
        },
        "KEY_PREFIX": env.str("REDIS_KEY_PREFIX", ""),
        "VERSION": 1,
    },
    "disk": {
        "BACKEND": "common.cache.disk.cache_backends.ExtendedDiskCache",
        "LOCATION": "_disk_cache",
        "TIMEOUT": env.int("DISK_CACHE_TIMEOUT", 300),
        "SHARDS": env.int("DISK_CACHE_SHARDS", 8),
        "DATABASE_TIMEOUT": env.float("DISK_CACHE_DATABASE_TIMEOUT", 0.010),
        "OPTIONS": {
            "size_limit": env.int("DISK_CACHE_SIZE_LIMIT", 2**30),  # 1 gigabyte
            "COMPRESSOR": "common.cache.compressors.Lz4Compressor",
            "SERIALIZER": "common.cache.serializers.PickleSerializer",
            "PICKLE_VERSION": -1,
        },
    },
}

IP2LOCATION_DATABASE_PATH = env.str("IP2LOCATION_DATABASE_PATH")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 10),
    ),  # 指定token有效期
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 30),
    ),  # 指定token刷新有效期
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHMS": ["HS256"],  # 指定加密的哈希函数
    "VERIFY_SIGNATURE": True,  # 开启验证密钥
    "VERIFY_EXP": True,  # 开启验证token是否过期
    "AUDIENCE": None,
    "ISSUER": "saas",
    "LEEWAY": 0,
    "REQUIRE": ["exp"],
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "SIGNING_KEY": env.str("JWT_SIGNING_KEY"),
}

LOGIN_MAX_ATTEMPTS = env.int("LOGIN_MAX_ATTEMPTS", 5)
LOGIN_LOCKOUT_TIME = env.int("LOGIN_LOCKOUT_TIME", 7200)

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = env.list("CELERY_ACCEPT_CONTENT")
CELERY_TASK_SERIALIZER = env.str("CELERY_TASK_SERIALIZER")
CELERY_RESULT_SERIALIZER = env.str("CELERY_RESULT_SERIALIZER")
CELERY_RESULT_BACKEND = "tasks.backends.CeleryResultBackend"
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = env.str("CELERY_TIMEZONE")
# 任务是否总是本地执行
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", False)
# 每个 worker 子进程在执行多少任务后被销毁并重启。用于避免内存泄漏
CELERY_WORKER_MAX_TASKS_PER_CHILD = env.int("CELERY_WORKER_MAX_TASKS_PER_CHILD", 100)
CELERY_DEFAULT_ROUTING_KEY = "default"
CELERY_DEFAULT_QUEUE = "default"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
