from django.http import HttpResponse

def health_check_view(request): # Health check endpoint, always returns 200 OK
    return HttpResponse("OK", status=200)