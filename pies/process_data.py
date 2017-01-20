import ast
import csv
import itertools
import json
from operator import itemgetter
import os
import string
import re

from collections import Counter
import enum

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView




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


def prep_text(file):
	
	first_step = open(file).read().strip().split('\n')

	return first_step



def process(text, tokenizer=TweetTokenizer(), stopwords=[]):

	text = text.lower()
	tokens = tokenizer.tokenize(text)

	return [tok for tok in tokens if tok not in stopword_list and not tok.isdigit()]



# make sure tweets don't break the database
def sanitize(word):
	regex = re.compile('[^a-zA-Z/\s]')
	clean_word = regex.sub('', word)
	
	return clean_word




def ready_tweets_for_emolex(file):
	first_step = prep_text(file)
	
	tokenized_tweets = []

	for tweet in first_step:
		second_step = process(tweet)
		tokenized_tweets.append(second_step)
	return tokenized_tweets




# NEEDED FOR CLASSIFY
def query_emolex(host, database, user, password, tweet_word):

	cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
	cursor = cnx.cursor(dictionary=True)

	clean_tweet_word = sanitize(tweet_word)
	
	query = "SELECT w.word, e.emotion, w.count, wes.score, wes.word_id, wes.emotion_id, w.id, e.id FROM words w JOIN word_emotion_score wes ON wes.word_id = w.id JOIN emotions e ON e.id = wes.emotion_id WHERE w.word = %s"

	cursor.execute(query, [clean_tweet_word])

	results = cursor.fetchall()

	emotion_list = []

	for emotion in results:
		average_score = emotion['score']/emotion['count']
		emotion_w_score = (emotion['emotion'], average_score)
		emotion_list.append(emotion_w_score)

	return emotion_list


	cursor.close()
	cnx.close()

# print(query_emolex(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, 'baby'))
# NEEDED FOR CLASSIFY
def find_strongest_emotion_for_word(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet_word):

	emotion_list = query_emolex(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet_word)
	final_scoring = []
	if emotion_list:
		highest_scoring_emotion = max(emotion_list, key=itemgetter(1))[0]
		highest_score = max(emotion_list, key=itemgetter(1))[1]
		final_scoring.append(highest_scoring_emotion)
		final_scoring.append(highest_score)
		return final_scoring

# print(find_strongest_emotion_for_word(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, 'baby'))

# NEEDED FOR CLASSIFY 
def find_strongest_emotions_in_tweet(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, word_list):
	emotion_list = []

	for word in word_list:
		highest_scoring_emotion = find_strongest_emotion_for_word(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, word)

		if highest_scoring_emotion:
			emotion_list.append(highest_scoring_emotion)
	
	return emotion_list

get_ready = ready_tweets_for_emolex('rose_test_raw.txt')

# print(get_ready)

def show_top_emotion(emotion_array):

	emotion_hash = {"anger": 0, "anticipation": 0, "disgust": 0, "fear": 0, "joy": 0, "negative": 0, "positive": 0, "sadness": 0, "surprise": 0, "trust": 0}

	for emotion in emotion_array:
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
	return emotion_hash


def set_go(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweets):
	tweets_and_feels = []
	disclaimer = 'Unable to process this tweet'
	for tweet in tweets:
		# results = dict()

		strongest_emotions = find_strongest_emotions_in_tweet(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, tweet)

		tweets_and_feels.append(show_top_emotion(strongest_emotions))
		# if strongest_emotions:
		# 	# results['emotions'] = show_top_emotion(strongest_emotions)
			
		# 	# tweets_and_feels.append(strongest_emotions)
		# 	tweets_and_feels.append(show_top_emotion(strongest_emotions))
		# else:
		# 	results['emotions'] = disclaimer
		# 	# tweets_and_feels.append(disclaimer)
		
		# 	tweets_and_feels.append(results)
	
	return tweets_and_feels




try_json = [{'emotions': {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'negative': 0, 'positive': 0, 'sadness': 1, 'surprise': 0, 'trust': 0}}, {'emotions': {'anger': 1, 'anticipation': 1, 'disgust': 2, 'fear': 0, 'joy': 1, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 1}}, {'emotions': {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 1}}]


x = open('testpie.csv').read()

print(x)

