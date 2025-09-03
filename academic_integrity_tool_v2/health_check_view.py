import logging
from django.http import HttpResponse
logger = logging.getLogger(__name__)

def health_check_view(request):
    """Health check endpoint, always returns 200 OK"""
    return HttpResponse("OK", status=200)