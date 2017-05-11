from nosycolors.settings.base import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATICFILES_DIR = (os.path.join(BASE_DIR, 'static'))

STATIC_URL = '/static/'

with open('.env') as secrets:
  lies = dict(ast.literal_eval(secrets.read()))
  
  SECRET_KEY = lies['SECRET_KEY']
  USER_NAME = lies['USER_NAME']
  DATABASE_NAME = lies['DATABASE_NAME']
  DATABASE_KEY = lies['DATABASE_KEY']
  CONSUMER_KEY = lies['CONSUMER_KEY']
  CONSUMER_SECRET = lies['CONSUMER_SECRET']
  ACCESS_TOKEN = lies['ACCESS_TOKEN']
  ACCESS_SECRET = lies['ACCESS_SECRET']
  CALLBACK_URL = lies['CALLBACK_URL']
  HOST = lies['HOST']
  PORT = lies['PORT']


DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']



TWITTER_AUTH = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

AUTHORIZED_USER = tweepy.API(TWITTER_AUTH, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

