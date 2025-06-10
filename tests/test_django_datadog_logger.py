"""Tests for `django_datadog_logger` package."""

import logging

from test_plus import TestCase

from django_datadog_logger.formatters.datadog import DataDogJSONFormatter


class DjangoDatadogLoggerTestCase(TestCase):
    def test_format_json_accepts_a_tuple_of_nones_as_exc_info(self):
        """
        When logger is called with exc_info=True, then the exc_info
        attribute of the LogRecord is a tuple of (None, None, None).
        """
        record = logging.LogRecord("foo", logging.ERROR, "foo.py", 42, "This is an error", None, (None, None, None))
        formatter = DataDogJSONFormatter()
        json_record = formatter.json_record("Foo", {}, record)

        self.assertEqual(json_record.get("error.kind"), None)


class RequestLoggingMiddlewareTestCase(TestCase):
    def test_log_entry_for_200_ok(self):
        with self.assertLogs("django_datadog_logger.middleware.request_log", level="INFO") as cm:
            self.get("ok")
            self.response_200()

    def test_log_entry_for_400_bad_request(self):
        with self.assertLogs("django_datadog_logger.middleware.request_log", level="INFO") as cm:
            self.get("bad")
            self.response_400()

    def test_log_entry_for_500_server_error(self):
        with self.assertLogs("django_datadog_logger.middleware.request_log", level="INFO") as cm:
            self.get("error")
            # django-test-plus does not have a convenience method for 500 errors,
            self.assertEqual(self.last_response.status_code, 500)
