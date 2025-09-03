import logging
from django.http import HttpResponse
logger = logging.getLogger(__name__)

def health_check_view(request): # Health c`heck endpoint, always returns 200 OK
    """
    A temporary health check view that logs all incoming headers to help debug
    issues with load balancers.
    """
    # Log all headers to the console for inspection
    logger.info("--- STARTING HEALTH CHECK HEADER LOG ---")
    for header, value in request.headers.items():
        logger.info(f"Header: {header}, Value: {value}")
    logger.info("--- ENDING HEALTH CHECK HEADER LOG ---")
    return HttpResponse("OK", status=200)