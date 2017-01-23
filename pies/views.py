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


# test_tweet1 = "@ZeroUtopia @democracynow Unfortunately his listening skills are not good enough for that level of meatiness. I'll probably do @BBC first"
test_tweet2 = "RT @SUPGVNetwork: A toddler has now shot a person every week in America for two years straight. Yes, you read that correctly. https://t.co…"
# test_tweet3 = "@ZeroUtopia I had to just grit my teeth and repeat in my head ... still better than FOX... still better than FOX.... UGH"
# test_tweet4 = "RT @quasimado: A quarter of 2016's mass shootings occurred when a woman was attempting to leave a relationship https://t.co/oOxZR7Ztth"
# test_tweets = [test_tweet1, test_tweet2, test_tweet3, test_tweet4]

# try_json = [{'emotions': {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'negative': 0, 'positive': 0, 'sadness': 1, 'surprise': 0, 'trust': 0}}, {'emotions': {'anger': 1, 'anticipation': 1, 'disgust': 2, 'fear': 0, 'joy': 1, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 1}}, {'emotions': {'anger': 0, 'anticipation': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'negative': 0, 'positive': 0, 'sadness': 0, 'surprise': 0, 'trust': 1}}]


# def pie_data(request):
# 	context = try_json[0]

# 	return render(request, 'pie_data.html', context)

class IndexView(TemplateView):
    template_name = "index.html"

class AboutView(TemplateView):
    template_name = "about.html"



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

#THIS ONE IS IN PROGRESS
# def get_pie_data(request):

# 	if request.method == 'POST':
# 	    # create a form instance and populate it with data from the request:
# 		form = HandleForm(request.POST)

# 		if form.is_valid():

# 			target_handle = form.cleaned_data['target_handle']
# 			number_of_tweets = form.cleaned_data['number_of_tweets']
			
# 			rawtweepy = settings.AUTHORIZED_USER.user_timeline(screen_name=target_handle, count=number_of_tweets)

				
# 			user = settings.AUTHORIZED_USER.get_user(screen_name=target_handle)
# 			target = dict()
# 			target['name'] = user.name
# 			target['screen_name'] = user.screen_name

# 			tweets = []

# 			for raw_tweet in rawtweepy:
# 				tweet = {}

# 				tweet_words = process(raw_tweet.text)
				
# 				strongest_emotions = find_strongest_emotions_in_tweet(settings.HOST, settings.DATABASE_NAME, settings.USER_NAME, settings.DATABASE_KEY, tweet_words)

# 				if strongest_emotions:
# 					# strongest_emotions = ", ".join(strongest_emotions)
# 					tweet['emotion'] = strongest_emotions
# 				else:
# 					tweet['emotion'] = 'Unable to process this tweet'

# 				tweet['text'] = (raw_tweet.text)

# 				tweets.append(tweet)



# 			context = {'target_handle': target_handle, 'tweets': tweets, 'target': target }

# # if a GET (or any other method) we'll create a blank form
# 	else:
# 		form = HandleForm()


# 	return context


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
			these_tweets = []
			all_emotion_list = []
			all_score_list = []
			all_color_scores = []
			for test_tweet in rawtweepy:
				one_score_list = []
				one_emotion_list = []
				tweet = {}
				tweet['text']= test_tweet.text
				tweet['id'] = test_tweet.id_str
				these_tweets.append(tweet)

				emotions = find_strongest_emotions_in_tweet(settings.HOST, settings.DATABASE_NAME, settings.USER_NAME, settings.DATABASE_KEY, test_tweet.text)

				# count = show_top_emotion(emotions)
				# color_score = {}
				# for emotion in count:
				# 	if emotion[1] > 0:
				# 		color_score[emotion[0]] = emotion[1]
				# 		one_emotion_list.append(emotion[0])
				# 		one_score_list.append(emotion[1])

				# all_emotion_list.append(one_emotion_list)
				# all_score_list.append(one_score_list)
				# all_color_scores.append(color_score)
				count = show_top_emotion(emotions)
				# color_score = {}
				# color_score['emotions'] = []
				# color_score['scores'] = []
				# tweet_color_scores = []
				for emotion in count:
					one_emotion_hash = {}
					# color_score[emotion[0]] = emotion[1]
					# one_emotion_list.append(emotion[0])
					# one_score_list.append(emotion[1])
					if emotion[1] > 0:
						one_emotion_list.append(emotion[0])
						one_emotion_hash['emotion'] = emotion[0]
						one_emotion_hash['score'] = emotion[1]
						one_emotion_hash['tweet_id'] = test_tweet.id
						one_emotion_hash['tweet_text'] = test_tweet.text
						those_tweets.append(one_emotion_hash)
					# color_score['emotions'].append(emotion[0])
					# color_score['scores'].append(emotion[1])
				# one_emotion_list.append(emotion[0])
				# one_score_list.append(emotion[1])

				# tweet_color_scores.append(color_score)

				# all_emotion_list.append(one_emotion_list)
				# all_score_list.append(one_score_list)
				# all_color_scores.append(tweet_color_scores)
				
				# tweet['emotions'] = one_emotion_list
				# tweet['scores'] = one_score_list
				
				# those_tweets.append(tweet)
				# print(those_tweets)
	# context = {'emotions': json.dumps(all_emotion_list), 'scores': all_score_list, 'target_handle': target_handle, 'target': target, 'those_tweets': json.dumps(those_tweets), 'these_tweets': json.dumps(these_tweets), 'color_scores': json.dumps(all_color_scores)}
	# # print(all_score_list)
	context = {'target_handle': target_handle, 'target': target, 'those_tweets': json.dumps(those_tweets), 'these_tweets': json.dumps(these_tweets)}
				# context = {'word': "smile"}
	return render(request, 'pie_data.html', context)

def test_pie(request):
	# context = {'data': [[2,4,2, 5], [2,4,2, 2]], 'emotions':[['anticipation', 'joy', 'trust', 'sadness'], ['surprise', 'anger', 'fear', 'disgust']]}
	# context = {'data': [[{'emotion': 'anticipation', 'score': 2}, {'emotion': 'joy', 'score': 4}, {'emotion': 'suprise', 'score': 2}], 
	# [{'emotion': 'anger', 'score': 2}, {'emotion': 'disgust', 'score': 4}, {'emotion': 'fear', 'score': 2}]]}
	# 	context = {'tweets': [{'anticipation': 2}, {'joy': 4}, {'suprise': 2}], 
	# [{'anger': 2}, {'disgust': 4}, {'fear': 2}]}
	# context = {'data': [{'scores': [2,4,2], 'emotions':['anticipation', 'joy', 'trust']}, {'emotions': ['surprise', 'anger', 'fear', 'disgust'], 'scores': [2, 4, 3, 1]}]}

	these_tweets = ['there once was a man from nantucket',  'sally sells sea shells by the seashore']



	those_tweets = [{'tweet_id': 1234, 'emotion': 'anticipation', 'score': 2, 'tweet_text': 'gerber baby'}, {'tweet_id': 1234,'emotion': 'joy', 'score': 7, 'tweet_text': 'gerber baby'}, {'tweet_id': 1234,'emotion': 'sadness', 'score': 1, 'tweet_text': 'gerber baby'}, {'tweet_id': 456, 'emotion': 'anger', 'score': 2, 'tweet_text': 'gerber baby'}, {'tweet_id': 456, 'emotion': 'disgust', 'score': 4, 'tweet_text': 'no way'}, {'tweet_id': 456, 'emotion': 'fear', 'score': 2, 'tweet_text': 'no way'}]

	context = {'those_tweets': json.dumps(those_tweets), 'these_tweets': these_tweets}

	return render(request, 'test_pie.html', context)




