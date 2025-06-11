from django.urls import path

from tests import views

urlpatterns = [
    path("ok/", views.ok_view, name="ok"),
    path("bad/", views.bad_request_view, name="bad"),
    path("error/", views.server_error_view, name="error"),
]
