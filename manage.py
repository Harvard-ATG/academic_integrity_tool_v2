#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'test' in sys.argv:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'academic_integrity_tool_v2.settings.test'
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_integrity_tool_v2.settings.aws')

    # --- ADD THIS CHECK HERE ---
    try:
        from .utils.redis_startup_check import check_redis_connection
        check_redis_connection()
    except ImportError:
        # Fallback if the file is not in .utils, or if the check is not desired in production.
        print("Warning: Redis startup check module not found. Skipping check.")
    
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
