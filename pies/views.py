import csv

import json
import logging
import os
from operator import itemgetter
import re
import string


from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
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

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

class AboutView(TemplateView):
    template_name = "about.html"



def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

# NEEDED FOR CLASSIFY
def process(text, tokenizer=TweetTokenizer(), stopwords=[]):

	text = text.lower()
	tokens = tokenizer.tokenize(text)

	return [tok for tok in tokens if tok not in stopword_list and not tok.isdigit()]


# NEEDED FOR CLASSIFY
def query_emolex(host, database, user, password, tweet):

	cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
	cursor = cnx.cursor(dictionary=True)
	tweet_words = process(tweet)
# make sure tweets don't break the database
	regex = re.compile('[^a-zA-Z]')

	for i in range(len(tweet_words)):
		tweet_words[i] = regex.sub('', tweet_words[i])


	query = "SELECT w.word, e.emotion, w.count, wes.score, wes.word_id, wes.emotion_id, w.id, e.id FROM words w JOIN word_emotion_score wes ON wes.word_id = w.id JOIN emotions e ON e.id = wes.emotion_id WHERE w.word IN (%s)"
 
	in_p=', '.join(list(map(lambda x: '%s', tweet_words)))

	query = query % in_p

	cursor.execute(query, tuple(tweet_words))

	results = cursor.fetchall()

	cursor.close()
	cnx.close()

	emotion_list = dict()

	for word in results:
		if word['word'] not in emotion_list:
			emotion_list[word['word']] = []
		
		average_score = word['score']/word['count']
		emotion_w_score = (word['emotion'], average_score)
		emotion_list[word['word']].append(emotion_w_score)

	return emotion_list



def find_strongest_emotions_in_tweet(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet):

	emotion_list = query_emolex(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet)
	final_scoring = dict()

	for word in emotion_list:
		highest_scoring_emotion = max(emotion_list[word], key=itemgetter(1))[0]
		highest_score = max(emotion_list[word], key=itemgetter(1))[1]

		final_scoring[word] = (highest_scoring_emotion, highest_score)
	print(final_scoring)
	return final_scoring




def show_top_emotion(emotion_dictionary):
	emotion_hash = {"anger": 0, "anticipation": 0, "disgust": 0, "fear": 0, "joy": 0, "sadness": 0, "surprise": 0, "trust": 0}

	for word in emotion_dictionary:
		emotion = emotion_dictionary[word]
		if emotion[0] == 'anger':
			emotion_hash['anger'] += 1
		if emotion[0] == 'anticipation':
			emotion_hash['anticipation'] += 1
		if emotion[0] == 'disgust':
			emotion_hash['disgust'] += 1
		if emotion[0] == 'fear':
			emotion_hash['fear'] += 1
		if emotion[0] == 'joy':
			emotion_hash['joy'] += 1
		if emotion[0] == 'sadness':
			emotion_hash['sadness'] += 1
		if emotion[0] == 'surprise':
			emotion_hash['surprise'] += 1
		if emotion[0] == 'trust':
			emotion_hash['trust'] += 1
	return emotion_hash.items()


def pie_data(request):

	if request.method == 'POST':
		form = HandleForm(request.POST)

		if form.is_valid():

			target_handle = form.cleaned_data['target_handle']
			number_of_tweets = form.cleaned_data['number_of_tweets']
			
			rawtweepy = settings.AUTHORIZED_USER.user_timeline(screen_name=target_handle, count=number_of_tweets)

				
			user = settings.AUTHORIZED_USER.get_user(screen_name=target_handle)

			target = dict()
			target['name'] = user.name
			target['screen_name'] = user.screen_name

			all_tweet_emotions = []
			all_tweet_details = []

			for test_tweet in rawtweepy:

				tweet = {}
				tweet['text']= test_tweet.text
				tweet['id'] = test_tweet.id_str
				# tweet['date'] = utc_to_local(test_tweet.created_at)

				all_tweet_details.append(tweet)

				emotions = find_strongest_emotions_in_tweet(os.environ['HOST'], os.environ['DATABASE_NAME'], os.environ['USER_NAME'], os.environ['DATABASE_KEY'], test_tweet.text)

				count = show_top_emotion(emotions)

				for emotion in count:
					one_emotion_hash = {}

					if emotion[1] > 0:
						one_emotion_hash['emotion'] = emotion[0]
						one_emotion_hash['score'] = emotion[1]
						one_emotion_hash['tweet_id'] = test_tweet.id
						one_emotion_hash['tweet_text'] = test_tweet.text

						all_tweet_emotions.append(one_emotion_hash)
  
		context = {'target': target, 'tweet_emotions': json.dumps(all_tweet_emotions), 'tweet_details': json.dumps(all_tweet_details)}

		return render(request, 'pie_data.html', context)

def test_pie(request):

	these_tweets = ['there once was a man from nantucket',  'sally sells sea shells by the seashore']

	those_tweets = [{'tweet_id': 1234, 'emotion': 'anticipation', 'score': 2, 'tweet_text': 'gerber baby'}, {'tweet_id': 1234,'emotion': 'joy', 'score': 7, 'tweet_text': 'gerber baby'}, {'tweet_id': 1234,'emotion': 'sadness', 'score': 1, 'tweet_text': 'gerber baby'}, {'tweet_id': 456, 'emotion': 'anger', 'score': 2, 'tweet_text': 'gerber baby'}, {'tweet_id': 456, 'emotion': 'disgust', 'score': 4, 'tweet_text': 'no way'}, {'tweet_id': 456, 'emotion': 'fear', 'score': 2, 'tweet_text': 'no way'}]

	context = {'those_tweets': json.dumps(those_tweets), 'these_tweets': these_tweets}

	return render(request, 'test_pie.html', context)




