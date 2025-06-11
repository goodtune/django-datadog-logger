"""
Minimal Django settings and test views for middleware testing.
"""

SECRET_KEY = "test"

DEBUG = True

ROOT_URLCONF = "tests.urls"

ALLOWED_HOSTS = ["*"]

TEST_RUNNER = "django.test.runner.DiscoverRunner"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = [
    "django_datadog_logger.middleware.request_id.RequestIdMiddleware",
    "django_datadog_logger.middleware.error_log.ErrorLoggingMiddleware",
    "django_datadog_logger.middleware.request_log.RequestLoggingMiddleware",
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

DJANGO_DATADOG_LOGGER_EXTRA_INCLUDE = r"^django_datadog_logger\..*"
