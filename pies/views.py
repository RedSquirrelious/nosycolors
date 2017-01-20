import csv

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


class IndexView(TemplateView):
    template_name = "index.html"

class AboutView(TemplateView):
    template_name = "about.html"


# test_tweet1 = "@ZeroUtopia @democracynow Unfortunately his listening skills are not good enough for that level of meatiness. I'll probably do @BBC first"
# test_tweet2 = "RT @SUPGVNetwork: A toddler has now shot a person every week in America for two years straight. Yes, you read that correctly. https://t.co…"
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
def query_emolex(host, database, user, password, tweet_word):

	cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
	cursor = cnx.cursor(dictionary=True)

# make sure tweets don't break the database
	regex = re.compile('[^a-zA-Z/\s]')
	clean_tweet_word = regex.sub('', tweet_word)
	
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





# NEEDED FOR CLASSIFY 
def find_strongest_emotions_in_tweet(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, word_list):
	emotion_list = []
	
	for word in word_list:
		highest_scoring_emotion = find_strongest_emotion_for_word(HOST, DATABASE_NAME, USER_NAME, DATABASE_KEY, word)

		if highest_scoring_emotion:
			emotion_list.append(highest_scoring_emotion)
	
	return emotion_list

def show_top_emotion(emotion_array):
	emotion_hash = {"anger": 0, "anticipation": 0, "disgust": 0, "fear": 0, "joy": 0, "sadness": 0, "surprise": 0, "trust": 0}

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
	return emotion_hash.items()



#THIS ONE IS IN PROGRESS
def get_pie_data(request):

	if request.method == 'POST':
	    # create a form instance and populate it with data from the request:
		form = HandleForm(request.POST)

		if form.is_valid():

			target_handle = form.cleaned_data['target_handle']
			number_of_tweets = form.cleaned_data['number_of_tweets']
			
			rawtweepy = settings.AUTHORIZED_USER.user_timeline(screen_name=target_handle, count=number_of_tweets)

				
			user = settings.AUTHORIZED_USER.get_user(screen_name=target_handle)
			target = dict()
			target['name'] = user.name
			target['screen_name'] = user.screen_name

			tweets = []

			for raw_tweet in rawtweepy:
				tweet = {}

				tweet_words = process(raw_tweet.text)
				
				strongest_emotions = find_strongest_emotions_in_tweet(settings.HOST, settings.DATABASE_NAME, settings.USER_NAME, settings.DATABASE_KEY, tweet_words)

				if strongest_emotions:
					# strongest_emotions = ", ".join(strongest_emotions)
					tweet['emotion'] = strongest_emotions
				else:
					tweet['emotion'] = 'Unable to process this tweet'

				tweet['text'] = (raw_tweet.text)

				tweets.append(tweet)



			context = {'target_handle': target_handle, 'tweets': tweets, 'target': target }

# if a GET (or any other method) we'll create a blank form
	else:
		form = HandleForm()


	return context


#THIS ONE WORKS
def pie_data(request):
	if request.method == 'POST':
	    # create a form instance and populate it with data from the request:
		form = HandleForm(request.POST)

		if form.is_valid():

			target_handle = form.cleaned_data['target_handle']
			number_of_tweets = form.cleaned_data['number_of_tweets']
			
			rawtweepy = settings.AUTHORIZED_USER.user_timeline(screen_name=target_handle, count=number_of_tweets)

				
			user = settings.AUTHORIZED_USER.get_user(screen_name=target_handle)
			target = dict()
			target['name'] = user.name
			target['screen_name'] = user.screen_name

			those_tweets = []

			all_emotion_list = []
			all_score_list = []
			
			for test_tweet in rawtweepy:
				one_score_list = []
				one_emotion_list = []
				tweet = {}
				tweet['text']= test_tweet.text

				first_pass = process(test_tweet.text)
				# print(first_pass)
				emotions = find_strongest_emotions_in_tweet(settings.HOST, settings.DATABASE_NAME, settings.USER_NAME, settings.DATABASE_KEY, first_pass)
				# print(emotions)
				count = list(show_top_emotion(emotions))
				# print(count)
				for emotion in count:
					if emotion[1] > 0:
						one_emotion_list.append(emotion[0])
						one_score_list.append(emotion[1])

				all_score_list.append(one_score_list)
				tweet['emotion'] = one_emotion_list
				those_tweets.append(tweet)
	# print(all_score_list)
	context = {'emotions': all_emotion_list, 'scores': all_score_list, 'target_handle': target_handle, 'target': target, 'tweets': those_tweets}

	return render(request, 'pie_data.html', context)

