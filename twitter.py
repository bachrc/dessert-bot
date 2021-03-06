# coding: utf8
import base64
import logging
import time
import json

import oauth2 as oauth

import httplib2

import urllib

import twitter_settings

class TwitterError(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
    def __str__(self):
        return "Twitter returned " + str(self.status_code) + " : " + self.content


def get_mentions(since=-1):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    
    if since > -1:
        resp, content = client.request("https://api.twitter.com/1.1/statuses/mentions_timeline.json?count=800&since_id=" + str(since), "GET")
    else:
        resp, content = client.request("https://api.twitter.com/1.1/statuses/mentions_timeline.json?count=200", "GET")
    
    if resp.status != 200:
        raise TwitterError(resp.status, content)
    
    return json.loads(content)

def get_tweets(screen_name, auth=True):
    if auth:
        client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    else:
        client = httplib2.Http(timeout=30)

    resp, content = client.request('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=' + screen_name + '&count=800&trim_user=true', "GET")
    
    if resp.status != 200:
        raise TwitterError(resp.status, content)
    
    return json.loads(content)

def get_tweet(tweetID):
	client = oauth.Client(twitter_settings.consumer, twitter_settings.token)

	resp, content = client.request('https://api.twitter.com/1.1/statuses/show/{}.json'.format(tweetID), "GET")

	if resp.status != 200:
		raise TwitterError(resp.status, content)
    
	return json.loads(content)

def post_tweet(text, replyID = None, mediaID = None):
	print(text)
	args = [("status", text)]
	
	if replyID != None : args.append(("in_reply_to_status_id", replyID))
	if mediaID != None : args.append(("media_ids", mediaID))

	urlArgs = urllib.urlencode(args)

	client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
	resp, content = client.request("https://api.twitter.com/1.1/statuses/update.json", "POST", urlArgs)
	
	if resp.status != 200:
		raise TwitterError(resp.status, content)
	
	return content

def upload_buffer_photo(contenu):
	data = base64.b64encode(contenu)
	urlArgs = urllib.urlencode([("media_data", data)])
	
	client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
	resp, content = client.request("https://upload.twitter.com/1.1/media/upload.json", "POST", urlArgs)
	
	if resp.status != 200:
		raise TwitterError(resp.status, content)

	return json.loads(content)['media_id_string']

def upload_photo(imagePath):
	file = open(imagePath, 'rb')
	
	return upload_buffer_photo(file.read())
	
def post_photo(text, imagePath, replyID = None):	
	return post_tweet(text, replyID, upload_photo(imagePath))
	
def retweet_tweet(idTweet):
	print(idTweet)
	client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
	resp, content = client.request("https://api.twitter.com/1.1/statuses/retweet/{}.json".format(idTweet), "POST")
	if resp.status != 200:
		raise TwitterError(resp.status, content)
	
	return json.loads(content)
		
def search_tweet(text, nombreTweets = 1):
	urlArgs = urllib.urlencode([("q", unicode(text).encode('utf-8')),("count",nombreTweets)])
	
	client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
	resp, content = client.request("https://api.twitter.com/1.1/search/tweets.json?{}".format(urlArgs), "GET")
	
	if resp.status != 200:
		raise TwitterError(resp.status, content)
	
	return json.loads(content)