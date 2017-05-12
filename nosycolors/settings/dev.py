from nosycolors.settings.base import *


STATICFILES_DIR = (os.path.join(BASE_DIR, 'static'))

STATIC_URL = '/static/'


SECRET_KEY = os.environ['NC_SECRET_KEY']
USER_NAME = os.environ['NC_DB_USER']
DATABASE_NAME = os.environ['NC_DB_NAME']
DATABASE_KEY = os.environ['NC_DB_KEY']
CONSUMER_KEY = os.environ['NC_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['NC_CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['NC_ACCESS_TOKEN']
ACCESS_SECRET = os.environ['NC_ACCESS_SECRET']
CALLBACK_URL = os.environ['NC_CALLBACK_URL']
HOST = os.environ['NC_HOST']
PORT = os.environ['NC_PORT']

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.environ['NC_DB_NAME'],
    'USER': os.environ['NC_DB_USER'],
    'PASSWORD': os.environ['NC_DB_KEY'],
    'HOST': os.environ['NC_HOST'],
    'PORT': os.environ['NC_PORT'],
  }
  }

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']



TWITTER_AUTH = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

AUTHORIZED_USER = tweepy.API(TWITTER_AUTH, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

