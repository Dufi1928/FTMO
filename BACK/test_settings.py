from .settings import *

# Override database for tests to use in-memory SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for local apps to speed up tests and avoid conflicts
MIGRATION_MODULES = {
    'accounts': None,
    'teams': None,
    'matches': None,
}
