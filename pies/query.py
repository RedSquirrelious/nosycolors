import csv
import ast
import json

import os
from operator import itemgetter
import string
import re

from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.serializers.json import DjangoJSONEncoder

# from .forms import HandleForm


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




with open(os.path.dirname(__file__) + '../.env') as secrets:

	lies = dict(ast.literal_eval(secrets.read()))
	
	SECRET_KEY = lies['SECRET_KEY']
	USER_NAME = lies['USER_NAME']
	DATABASE_NAME = lies['DATABASE_NAME']
	DATABASE_KEY = lies['DATABASE_KEY']
	CONSUMER_KEY = lies['CONSUMER_KEY']
	CONSUMER_SECRET = lies['CONSUMER_SECRET']
	ACCESS_TOKEN = lies['ACCESS_TOKEN']
	ACCESS_SECRET =	lies['ACCESS_SECRET']
	CALLBACK_URL = lies['CALLBACK_URL']
	HOST = lies['HOST']


# test_tweet1 = "@ZeroUtopia @democracynow Unfortunately his listening skills are not good enough for that level of meatiness. I'll probably do @BBC first"
test_tweet2 = "RT @SUPGVNetwork: A toddler has now shot a person every week in America for two years straight. Yes, you read that correctly. https://t.co…"
# test_tweet3 = "@ZeroUtopia I had to just grit my teeth and repeat in my head ... still better than FOX... still better than FOX.... UGH"
# test_tweet4 = "RT @quasimado: A quarter of 2016's mass shootings occurred when a woman was attempting to leave a relationship https://t.co/oOxZR7Ztth"
# test_tweets = [test_tweet1, test_tweet2, test_tweet3, test_tweet4]

# try_json = [{'emotions': {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'negative': 0, 'positive': 0, 'sadness': 1, 'surprise': 0, 'trust': 0}}, {'emotions': {'anger': 1, 'anticipation': 1, 'disgust': 2, 'fear': 0, 'joy': 1, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 1}}, {'emotions': {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 1}}]


# def pie_data(request):
# 	context = try_json[0]

# 	return render(request, 'pie_data.html', context)



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
	# print(tweet_words)
	for i in range(len(tweet_words)):
		tweet_words[i] = regex.sub('', tweet_words[i])

	# print(tweet_words)
	query = "SELECT w.word, e.emotion, w.count, wes.score, wes.word_id, wes.emotion_id, w.id, e.id FROM words w JOIN word_emotion_score wes ON wes.word_id = w.id JOIN emotions e ON e.id = wes.emotion_id WHERE w.word IN (%s)"
 
	in_p=', '.join(list(map(lambda x: '%s', tweet_words)))

	query = query % in_p
	# print(query)
	cursor.execute(query, tuple(tweet_words))

	results = cursor.fetchall()
	# print(results)

	cursor.close()
	cnx.close()

	emotion_list = dict()

	for word in results:
		if word['word'] not in emotion_list:
			emotion_list[word['word']] = []
		average_score = word['score']/word['count']
		emotion_w_score = (word['emotion'], average_score)
		# emotion_list.append(emotion_w_score)	
		emotion_list[word['word']].append(emotion_w_score)


	return emotion_list

def find_strongest_emotion_for_wordlist(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet):

	emotion_list = query_emolex(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet)
	final_scoring = dict()

	for word in emotion_list:
		highest_scoring_emotion = max(emotion_list[word], key=itemgetter(1))[0]
		highest_score = max(emotion_list[word], key=itemgetter(1))[1]

		final_scoring[word] = (highest_scoring_emotion, highest_score)
	# print(final_scoring)
	return final_scoring


scott = find_strongest_emotion_for_wordlist(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, test_tweet2)

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

print(show_top_emotion(scott))

