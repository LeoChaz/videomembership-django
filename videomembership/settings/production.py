

import os
from django.conf import settings


#if not settings.DEBUG:
if not settings.DEBUG:
    #######
    # HEROKU

    # https://docs.djangoproject.com/en/1.9/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
        }
    }

    try:
        # Update database configuration with $DATABASE_URL.
        import dj_database_url
        db_from_env = dj_database_url.config()
        DATABASES['default'].update(db_from_env)
    except:
        pass

    # Update database configuration with $DATABASE_URL.
    #import dj_database_url
    #db_from_env = dj_database_url.config(conn_max_age=500)
    #DATABASES['default'].update(db_from_env)


    # #Static files (CSS, JavaScript, Images)
    # #https://docs.djangoproject.com/en/1.9/howto/static-files/
    #
    # PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    #
    # STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
    # STATIC_URL = '/static/'
    #
    # # Extra places for collectstatic to find static files.
    # STATICFILES_DIRS = (
    #     os.path.join(PROJECT_ROOT, 'static'),
    # )


    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

    ALLOWED_HOSTS = ['*']

    ######