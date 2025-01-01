from .base import *  # noqa

DEBUG = True  # noqa

INSTALLED_APPS += ["debug_toolbar"]  # noqa

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa

INTERNAL_IPS = [  # noqa
    "127.0.0.1",
]
