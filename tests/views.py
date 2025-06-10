from django.http import HttpResponseServerError, JsonResponse


def ok_view(request):
    return JsonResponse({"ok": True}, status=200)


def bad_request_view(request):
    return JsonResponse({"error": "bad request"}, status=400)


def server_error_view(request):
    return HttpResponseServerError("server error")
