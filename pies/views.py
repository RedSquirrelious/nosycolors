import csv

from datetime import datetime
import json
import logging

import os
from operator import itemgetter
import re
import string
import tweepy

from django.conf import settings, urls
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext, loader
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import TemplateView


from .forms import HandleForm


# FOR LANGUAGE ANALYSIS
## needed for MySQL

import mysql.connector
from mysql.connector import MySQLConnection, Error, connect, errorcode

## NLTK, language analysis
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import *
## import nltk.classify.util, nltk.metrics
from nltk import word_tokenize, sent_tokenize
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords


punct = list(string.punctuation)
stopword_list = stopwords.words('english') + punct + ['rt', 'via', '...', '…']

EMOTION_QUERY = "SELECT w.word, e.emotion, w.count, wes.score, wes.word_id, wes.emotion_id, w.id, e.id FROM words w JOIN word_emotion_score wes ON wes.word_id = w.id JOIN emotions e ON e.id = wes.emotion_id WHERE w.word IN (%s)"

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

class AboutView(TemplateView):
    template_name = "about.html"

class my404View(TemplateView):
    template_name = "404.html"

def validate_form(request):
    form = HandleForm(request.POST or None)  
    if request.method == 'POST':
      if form.is_valid():
        screen_name = form.cleaned_data['screen_name']
        number_of_tweets = form.cleaned_data['number_of_tweets']
      else:
        screen_name = ''
        number_of_tweets = ''   
      context = {'screen_name': screen_name, 'number_of_tweets': number_of_tweets}    
      return context


def tokenize_text(text, tokenizer=TweetTokenizer(), stopwords=[]):
    text = text.lower()
    tokens = tokenizer.tokenize(text)
    return [tok for tok in tokens if tok not in stopword_list and not tok.isdigit()]

def sanitize_text(tokens):
    regex = re.compile('[^a-zA-Z]')
    for i in range(len(tokens)):
      tokens[i] = regex.sub('', tokens[i])
    return tokens

def prepare_query(tweet_tokens):
    in_p=', '.join(list(map(lambda x: '%s', tweet_tokens)))
    query = EMOTION_QUERY % in_p
    return query

def query_emolex(host, database, user, password, query, tweet_tokens):
    cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(query, tuple(tweet_tokens))
    results = cursor.fetchall()
    cursor.close()
    cnx.close()
    return results

def tally_emotion_scores_by_word(emotion_list, results):
    for word in results:
      if word['word'] not in emotion_list:
        emotion_list[word['word']] = []      
      average_score = word['score']/word['count']
      emotion_w_score = (word['emotion'], average_score)
      emotion_list[word['word']].append(emotion_w_score)
    return emotion_list


def find_strongest_emotions_in_tweet(emotion_list):
    final_scoring = dict()
    for word in emotion_list:
      highest_scoring_emotion = max(emotion_list[word], key=itemgetter(1))[0]
      highest_score = max(emotion_list[word], key=itemgetter(1))[1]
      final_scoring[word] = (highest_scoring_emotion, highest_score)
    return final_scoring




def score_emotions(emotion_list):
    emotion_scores = {"anger": 0, "anticipation": 0, "disgust": 0, "fear": 0, "joy": 0, "sadness": 0, "surprise": 0, "trust": 0}
    for word in emotion_list:
      emotion = emotions[word]
      if emotion[0] == 'anger':
        emotion_scores['anger'] += 1
      if emotion[0] == 'anticipation':
        emotion_scores['anticipation'] += 1
      if emotion[0] == 'disgust':
        emotion_scores['disgust'] += 1
      if emotion[0] == 'fear':
        emotion_scores['fear'] += 1
      if emotion[0] == 'joy':
        emotion_scores['joy'] += 1
      if emotion[0] == 'sadness':
        emotion_scores['sadness'] += 1
      if emotion[0] == 'surprise':
        emotion_scores['surprise'] += 1
      if emotion[0] == 'trust':
        emotion_scores['trust'] += 1
    return emotion_scores.items()

def get_tweets(user_id, number_of_tweets):
    try:
      rawtweepy = settings.AUTHORIZED_USER.user_timeline(user_id=user_id, count=number_of_tweets)
      return raw_tweepy
    except tweepy.TweepError as e:
      print (getExceptionMessage(e.reason))
      pass  

def process_tweet_details(raw_tweepy):
    all_tweet_details = []
    for raw_tweet in rawtweepy:
      tweet = {}
      tweet['text'] = raw_tweet.text
      tweet['id'] = raw_tweet.id_str
      tweet['created_at'] = str(raw_tweet.created_at)
      tweet['user'] = raw_tweet.user.name
      tweet['screen_name'] = raw_tweet.user.screen_name
      all_tweet_details.append(tweet)
    return all_tweet_details



def process_emotions(all_tweet_emotions, emotion_scores, raw_tweet_id, raw_tweet_text):
    for emotion in emotion_scores:
      one_emotion_hash = {}
      if emotion[1] > 0:
        one_emotion_hash['emotion'] = emotion[0]
        one_emotion_hash['score'] = emotion[1]
        one_emotion_hash['tweet_id'] = raw_tweet_id
        one_emotion_hash['tweet_text'] = raw_tweet_text
        all_tweet_emotions.append(one_emotion_hash)


def construct_view_context(user_id, number_of_tweets):
    raw_tweepy = get_tweets(user_id, number_of_tweets)
    all_tweet_details = process_tweet_details(raw_tweepy)

    all_tweet_emotions = []
    emotion_list = dict()

    for raw_tweet in raw_tweepy:
      tweet_tokens = tokenize_text(raw_tweet.text)
      sanitized_tokens = sanitize_text(tweet_tokens)
      query = prepare_query(sanitized_tokens)
      word_emotion_results = query_emolex(settings.HOST, settings.DATABASE_NAME, settings.USER_NAME, settings.DATABASE_KEY, query, sanitized_tokens)
      emotions_most_strongly_associated = tally_emotion_scores_by_word(emotion_list, word_emotion_results)
      highest_emotion_scores = score_emotions(emotions_most_strongly_associated)
      top_emotion_scores = find_strongest_emotions_in_tweet(highest_emotion_scores)
      process_emotions(all_tweet_emotions, top_emotion_scores, raw_tweet.id, raw_tweet.text)


    context = {'tweet_emotions': all_tweet_emotions, 'tweet_details': all_tweet_details}
    return context


def pie_data(request):

  form_data = validate_form(request)

  if not form_data['screen_name']:
    messages.error(request, 'Please try again. Twitter handles must be alphanumeric (except for a starting "@"). Requested # of tweets must be > 0')
    return HttpResponseRedirect('/')

  try:
    print("HELLO")
    user = settings.AUTHORIZED_USER.get_user(screen_name=form_data['screen_name'])
    print("GOODBYE")
    view_context_data = construct_view_context(user.id, form_data['number_of_tweets'])

    context = {'tweet_emotions': json.dumps(view_context_data['tweet_emotions']), 'tweet_details': json.dumps(view_context_data['tweet_details'])}
    
    return render(request, 'pie_data.html', context)

  except tweepy.TweepError as e:
    emsg = e.api_code
    print(emsg)
    handle_tweepy_errors(request, emsg)










def test_pie(request):

  these_tweets = ['there once was a man from nantucket',  'sally sells sea shells by the seashore']

  those_tweets = [{'tweet_id': 1234, 'emotion': 'anticipation', 'score': 2, 'tweet_text': 'gerber baby'}, {'tweet_id': 1234,'emotion': 'joy', 'score': 7, 'tweet_text': 'gerber baby'}, {'tweet_id': 1234,'emotion': 'sadness', 'score': 1, 'tweet_text': 'gerber baby'}, {'tweet_id': 456, 'emotion': 'anger', 'score': 2, 'tweet_text': 'gerber baby'}, {'tweet_id': 456, 'emotion': 'disgust', 'score': 4, 'tweet_text': 'no way'}, {'tweet_id': 456, 'emotion': 'fear', 'score': 2, 'tweet_text': 'no way'}]

  context = {'those_tweets': json.dumps(those_tweets), 'these_tweets': these_tweets}

  return render(request, 'test_pie.html', context)


def hash_pie(request):
  if request.method == 'POST':
    form = HandleForm(request.POST)

    if form.is_valid():

      screen_name = form.cleaned_data['screen_name']
      number_of_tweets = form.cleaned_data['number_of_tweets']
  
      hashtaggery = settings.AUTHORIZED_USER.search(q=screen_name, lang='en')

      all_tweet_details = []
      all_tweet_emotions = []

      for tweet in hashtaggery:
        hash_tweet = dict()
        hash_tweet['text'] = tweet.text
        hash_tweet['created_at'] = str(tweet.created_at)
        hash_tweet['user'] = tweet.user.name
        all_tweet_details.append(hash_tweet)

        emotions = find_strongest_emotions_in_tweet(settings.HOST, settings.DATABASE_NAME, settings.USER_NAME, settings.DATABASE_KEY, tweet.text)

        count = show_top_emotion(emotions)

        for emotion in count:
          one_emotion_hash = {}

          if emotion[1] > 0:
            one_emotion_hash['emotion'] = emotion[0]
            one_emotion_hash['score'] = emotion[1]
            one_emotion_hash['tweet_id'] = tweet.id
            one_emotion_hash['tweet_text'] = tweet.text

            all_tweet_emotions.append(one_emotion_hash)

      context = {'tweet_emotions': all_tweet_emotions, 'tweet_details': all_tweet_details}
    else:
      return request
  return render(request, 'hash_pie.html/', context)

def handle_tweepy_errors(request, code):
  if code == 50:
    messages.error(request, 'That user is not on Twitter')
    print('EEEEK')
    return bad_request(request)

def bad_request(request):
  print("UGHGHGHGHHGHG %s " %request)
  template = loader.get_template('index.html')
  messages.error(request, 'No such user')
  # request.method = 'GET'
  # request.path = '/'
  form = HandleForm()
  context = RequestContext(request)
  # response = HttpResponse(template.render(context))
  # # render_to_response(request, '/', RequestContext(request))
  # # response.path = '/'
  # response.status_code = 400
  response =  HttpResponseNotFound('<h1>Page not found</h1>')
  return response
