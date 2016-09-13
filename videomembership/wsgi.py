"""


It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "videomembership.settings")

application = get_wsgi_application()

# Si on est en prod (pas en debug) alors...
#if not settings.DEBUG:
if not settings.DEBUG:
    try:
        # HEROKU
        from whitenoise.django import DjangoWhiteNoise
        application = DjangoWhiteNoise(application)
    except:
        pass