from nosycolors.settings.base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATICFILES_DIR = (os.path.join(BASE_DIR, 'static'))

STATIC_URL = '/static/'

# with open('.env') as secrets:
#   lies = dict(ast.literal_eval(secrets.read()))
  
#   SECRET_KEY = lies['SECRET_KEY']
#   USER_NAME = lies['USER_NAME']
#   DATABASE_NAME = lies['DATABASE_NAME']
#   DATABASE_KEY = lies['DATABASE_KEY']
#   CONSUMER_KEY = lies['CONSUMER_KEY']
#   CONSUMER_SECRET = lies['CONSUMER_SECRET']
#   ACCESS_TOKEN = lies['ACCESS_TOKEN']
#   ACCESS_SECRET = lies['ACCESS_SECRET']
#   CALLBACK_URL = lies['CALLBACK_URL']
#   HOST = lies['HOST']
#   PORT = lies['PORT']

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

