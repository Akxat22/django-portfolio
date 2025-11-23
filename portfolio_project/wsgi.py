"""
WSGI config for portfolio_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import socket # <--- Import socket

# --- RENDER FIX: FORCE IPv4 ---
# This must be here in wsgi.py to ensure it runs before Gunicorn workers start.
# It prevents [Errno 101] Network is unreachable by ignoring IPv6.
original_getaddrinfo = socket.getaddrinfo

def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if family == 0:
        family = socket.AF_INET
    return original_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = ipv4_getaddrinfo
# ------------------------------

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')

application = get_wsgi_application()