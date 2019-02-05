from nosycolors.settings.base import *
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ['SECRET_KEY']
USER_NAME = os.environ['DB_USER']
DATABASE_NAME = os.environ['DB_NAME']
DATABASE_KEY = os.environ['DB_KEY']
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
CALLBACK_URL = os.environ['CALLBACK_URL']
HOST = os.environ['HOST']
PORT = os.environ['PORT']
ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.environ['DB_NAME'],
    'USER': os.environ['DB_USER'],
    'PASSWORD': os.environ['DB_KEY'],
    'HOST': os.environ['HOST'],
    'PORT': os.environ['PORT'],
  }
}

DEBUG = False

TWITTER_AUTH = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

AUTHORIZED_USER = tweepy.API(TWITTER_AUTH, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

STATIC_ROOT = os.path.join(BASE_DIR, 'deployment', 'collected_static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'deployment', 'media')