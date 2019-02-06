import os
import ast
import logging

import tweepy
from tweepy import OAuthHandler, AppAuthHandler
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#STATICFILES_ROOT = (os.path.join(BASE_DIR, 'static'))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'deployment', 'collected_static')

APPINSIGHTS_INSTRUMENTATIONKEY = os.environ['APPINSIGHTS_INSTRUMENTATIONKEY']

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pies',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'applicationinsights.django.ApplicationInsightsMiddleware',
]

ROOT_URLCONF = 'nosycolors.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pies/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nosycolors.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

APPLICATION_INSIGHTS = {
    # (required) Your Application Insights instrumentation key
    'ikey': APPINSIGHTS_INSTRUMENTATIONKEY,

    # (optional) By default, request names are logged as the request method
    # and relative path of the URL.  To log the fully-qualified view names
    # instead, set this to True.  Defaults to False.
    'use_view_name': True,

    # (optional) To log arguments passed into the views as custom properties,
    # set this to True.  Defaults to False.
    'record_view_arguments': False,

    # (optional) Exceptions are logged by default, to disable, set this to False.
    'log_exceptions': True,

    # (optional) Events are submitted to Application Insights asynchronously.
    # send_interval specifies how often the queue is checked for items to submit.
    # send_time specifies how long the sender waits for new input before recycling
    # the background thread.
    'send_interval': 1.0, # Check every second
    'send_time': 3.0, # Wait up to 3 seconds for an event
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # The application insights handler is here
        'appinsights': {
            'class': 'applicationinsights.django.LoggingHandler',
            'level': 'VERBOSE'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['appinsights'],
            'level': 'VERBOSE',
            'propagate': True,
        }
    }
}