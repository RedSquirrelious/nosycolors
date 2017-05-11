from nosycolors.settings.base import *

SECRET_KEY = os.environ['SECRET_KEY']


CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
CALLBACK_URL = os.environ['CALLBACK_URL']
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.environ['RDS_DB_NAME'],
    'USER': os.environ['RDS_USERNAME'],
    'PASSWORD': os.environ['RDS_PASSWORD'],
    'HOST': os.environ['RDS_HOSTNAME'],
    'PORT': os.environ['RDS_PORT'],
  }


DEBUG = False

ALLOWED_HOSTS = ['color-env.4yydtwdmva.us-west-2.elasticbeanstalk.com', 'www.redsquirrelious.io', 'redsquirrelious.io']

TWITTER_AUTH = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

AUTHORIZED_USER = tweepy.API(TWITTER_AUTH, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


STATIC_ROOT = os.path.join(BASE_DIR, 'deployment', 'collected_static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'deployment', 'media')