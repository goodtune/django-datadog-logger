"""Tests for `django_datadog_logger` package."""

import json
import logging
from unittest.mock import patch

import django
from django.test import Client
from freezegun import freeze_time
from test_plus import TestCase

from django_datadog_logger.formatters.datadog import DataDogJSONFormatter, DataDogJSONTestFormatter


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


@freeze_time("2023-10-01 12:00:00")
@patch("django_datadog_logger.middleware.request_id.generate_request_id", return_value="test-request-id")
class RequestLoggingMiddlewareTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client(headers={"User-Agent": "test-agent"})

    def format_records(self, records):
        formatter = DataDogJSONTestFormatter(self.last_response.wsgi_request)
        return [json.loads(formatter.format(record)) for record in records]

    def test_log_entry_for_200_ok(self, mock_generate_request_id):
        with self.assertLogs("django_datadog_logger.middleware.request_log", level="INFO") as cm:
            self.get("ok", data={"key": "val"})
            self.response_200()

        self.assertEqual(
            self.format_records(cm.records),
            [
                {
                    # ----------------------------------------
                    # These are set in DataDogJSONTestFormatter.json_record
                    # as baseline fields to the log_entry_dict.
                    # ----------------------------------------
                    "message": "HTTP 200 OK",
                    "logger.name": "django_datadog_logger.middleware.request_log",
                    "logger.thread_name": "MainThread",
                    "logger.method_name": "log_response",
                    "date": "2023-10-01T12:00:00+00:00",
                    "status": "INFO",
                    # ----------------------------------------
                    # These are from the wsgi request; listed in the order they
                    # are added in DataDogJSONTestFormatter.json_record
                    # ----------------------------------------
                    "network.client.ip": "127.0.0.1",
                    "http.url": "/ok/?key=val",
                    "http.url_details.host": "testserver",
                    "http.url_details.port": None,
                    "http.url_details.path": "/ok/",
                    "http.url_details.queryString": {"key": "val"},
                    "http.url_details.scheme": "http",
                    "http.url_details.view_name": "ok",
                    "http.request_id": "test-request-id",
                    # "usr.session_id": None,
                    # "usr.client_id": None,
                    # "usr.id": None,
                    # "usr.name": None,
                    # "usr.email": None,
                    # "usr.session_key": None,
                    "duration": 0.0,
                    # "db.statement": None,
                    # ----------------------------------------
                    # These fields are from the RequestLoggingMiddleware.log_response method
                    # ----------------------------------------
                    "http.status_code": 200,
                    "http.accept": None,
                    "http.method": "GET",
                    "http.referer": None,
                    "http.request_version": None,
                    "http.useragent": None if django.VERSION < (4, 0) else "test-agent",
                }
            ],
        )

    def test_log_entry_for_400_bad_request(self, mock_generate_request_id):
        with self.assertLogs("django_datadog_logger.middleware.request_log", level="INFO") as cm:
            self.get("bad", data={"key": "val"})
            self.response_400()

        self.assertEqual(
            self.format_records(cm.records),
            [
                {
                    # ----------------------------------------
                    # These are set in DataDogJSONTestFormatter.json_record
                    # as baseline fields to the log_entry_dict.
                    # ----------------------------------------
                    "message": "HTTP 400 Bad Request",
                    "logger.name": "django_datadog_logger.middleware.request_log",
                    "logger.thread_name": "MainThread",
                    "logger.method_name": "log_response",
                    "date": "2023-10-01T12:00:00+00:00",
                    "status": "WARNING",
                    # ----------------------------------------
                    # These are from the wsgi request; listed in the order they
                    # are added in DataDogJSONTestFormatter.json_record
                    # ----------------------------------------
                    "network.client.ip": "127.0.0.1",
                    "http.url": "/bad/?key=val",
                    "http.url_details.host": "testserver",
                    "http.url_details.path": "/bad/",
                    "http.url_details.port": None,
                    "http.url_details.queryString": {"key": "val"},
                    "http.url_details.scheme": "http",
                    "http.url_details.view_name": "bad",
                    "http.request_id": "test-request-id",
                    # "usr.session_id": None,
                    # "usr.client_id": None,
                    # "usr.id": None,
                    # "usr.name": None,
                    # "usr.email": None,
                    # "usr.session_key": None,
                    "duration": 0.0,
                    # "db.statement": None,
                    # ----------------------------------------
                    # These fields are from the RequestLoggingMiddleware.log_response method
                    # ----------------------------------------
                    "http.status_code": 400,
                    "error.kind": 400,
                    "error.message": "Bad Request",
                    "http.accept": None,
                    "http.method": "GET",
                    "http.referer": None,
                    "http.request_version": None,
                    "http.useragent": None if django.VERSION < (4, 0) else "test-agent",
                }
            ],
        )

    def test_log_entry_for_500_server_error(self, mock_generate_request_id):
        with self.assertLogs("django_datadog_logger.middleware.request_log", level="INFO") as cm:
            self.get("error", data={"key": "val"})
            # django-test-plus does not have a convenience method for 500 errors,
            self.assertEqual(self.last_response.status_code, 500)

        self.assertEqual(
            self.format_records(cm.records),
            [
                {
                    # ----------------------------------------
                    # These are set in DataDogJSONTestFormatter.json_record
                    # as baseline fields to the log_entry_dict.
                    # ----------------------------------------
                    "message": "HTTP 500 Internal Server Error",
                    "logger.name": "django_datadog_logger.middleware.request_log",
                    "logger.thread_name": "MainThread",
                    "logger.method_name": "log_response",
                    "date": "2023-10-01T12:00:00+00:00",
                    "status": "ERROR",
                    # ----------------------------------------
                    # These are from the wsgi request; listed in the order they
                    # are added in DataDogJSONTestFormatter.json_record
                    # ----------------------------------------
                    "network.client.ip": "127.0.0.1",
                    "http.url": "/error/?key=val",
                    "http.url_details.host": "testserver",
                    "http.url_details.port": None,
                    "http.url_details.path": "/error/",
                    "http.url_details.queryString": {"key": "val"},
                    "http.url_details.scheme": "http",
                    "http.url_details.view_name": "error",
                    "http.request_id": "test-request-id",
                    # "usr.session_id": None,
                    # "usr.client_id": None,
                    # "usr.id": None,
                    # "usr.name": None,
                    # "usr.email": None,
                    # "usr.session_key": None,
                    "duration": 0.0,
                    # "db.statement": None,
                    # ----------------------------------------
                    # These fields are from the RequestLoggingMiddleware.log_response method
                    # ----------------------------------------
                    "http.status_code": 500,
                    "error.kind": 500,
                    "error.message": "Internal Server Error",
                    "http.accept": None,
                    "http.method": "GET",
                    "http.referer": None,
                    "http.request_version": None,
                    "http.useragent": None if django.VERSION < (4, 0) else "test-agent",
                }
            ],
        )
