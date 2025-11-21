from .base import *

# region GENERAL ---------------------------------------------------------------

DEBUG = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# endregion --------------------------------------------------------------------

# region DATABASES -------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_NAME', default='postgres'),
        'HOST': env('POSTGRES_DB_HOST', default='localhost'),
        'PORT': env('POSTGRES_DB_PORT', default=5432),
        'USER': env('POSTGRES_USER', default='postgres'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='postgres'),
    }
}

# endregion --------------------------------------------------------------------

# region PASSWORDS -------------------------------------------------------------

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# endregion --------------------------------------------------------------------

# region CACHES ----------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '',
    },
}

# endregion --------------------------------------------------------------------
