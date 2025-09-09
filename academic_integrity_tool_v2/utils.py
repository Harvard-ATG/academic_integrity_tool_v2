import os
import socket
import requests
import logging
from typing import List

logger = logging.getLogger(__name__)

def get_ecs_task_ips() -> List[str]:
    """
    Retrieves the private IPv4 addresses of an ECS task's network interfaces.

    This function fetches metadata from the AWS ECS Task Metadata V4 endpoint,
    which is accessible via the ECS_CONTAINER_METADATA_URI_V4 environment
    variable that AWS automatically injects inside the container. It's designed to be used with the 'awsvpc'
    network mode to dynamically find the task's IPs, often for configuring
    application settings like Django's ALLOWED_HOSTS for load balancer health checks.

    Documentation: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v4.html
    Example v4 task metadata json response: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-metadata-endpoint-v4-response.html

    Returns:
        A list of unique private IPv4 address strings if successful,
        or an empty list if not running in ECS or if an error occurs.

    """
    ip_addresses = []
    metadata_url = os.environ.get('ECS_CONTAINER_METADATA_URI_V4')

    # If the environment variable is not set, we're not in a V4-enabled ECS task.
    if not metadata_url:
        logger.debug("ECS_CONTAINER_METADATA_URI_V4 not set; not running in ECS or not using V4 metadata.")
        return []

    try:
        # A slightly longer timeout is safer for the local network request.
        response = requests.get(f"{metadata_url}/task", timeout=2)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException:
        # Catches connection errors, timeouts, etc.
        return []

    task_metadata = response.json()
    if "Containers" in task_metadata:
        for container in task_metadata["Containers"]:
            if "Networks" in container:
                for network in container["Networks"]:
                    if network.get("NetworkMode") == "awsvpc" and "IPv4Addresses" in network:
                        ip_addresses.extend(network["IPv4Addresses"])

    # Return a list of unique IPs
    ip_address_list = list(set(ip_addresses))
    logger.debug(f"ECS task IP addresses: {ip_address_list}")
    return ip_address_list

def get_container_ip_from_socket():
    """
    Get the internal IP address of the current container.
    """
    ip = socket.gethostbyname(socket.gethostname())
    logger.debug(f"Container IP from socket {ip}")
    return ip

def parse_env_list(value, default=None):
    """
    Parse a comma-separated list from an environment variable.
    """
    if value:
        return [item.strip() for item in value.split(',')]
    return []