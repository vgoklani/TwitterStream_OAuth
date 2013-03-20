# http://developer.klout.com/io-docs

import requests
import datetime

def get_kloutID(twitter_screen_name, api_key):
	kloutID = requests.get( 'http://api.klout.com/v2/identity.json/twitter?screenName=%s&key=%s' % (twitter_screen_name, api_key) )
	return kloutID.json()

def get_klout_user_method(kloutID, method, api_key):
	assert method in ('score', 'topics', 'influence')
	r = requests.get( 'http://api.klout.com/v2/user.json/%s/%s?key=%s' % (kloutID, method, api_key) )
	return r.json()

def get_klout_data(twitter_screen_name, api_key):
	kloutID = get_kloutID(twitter_screen_name, api_key)['id']
	
	klout_score = get_klout_user_method(kloutID, 'score', api_key)
	klout_topics = [r['displayName'] for r in get_klout_user_method(kloutID, 'topics', api_key)]
	klout_influence = get_klout_user_method(kloutID, 'influence', api_key)

	influencers = [w['entity']['payload']['nick'] for w in klout_influence['myInfluencers']]
	influencees = [w['entity']['payload']['nick'] for w in klout_influence['myInfluencees']]
	
	return {'Twitter screen-name' : twitter_screen_name, 'Klout Score' : klout_score['score'], 'Klout Topics' : klout_topics, 'Klout Influencers':influencers, 'Klout Influencees':influencees, 'Klout Influencer Count' : klout_influence['myInfluencersCount'], 'Klout Influencee Count' : klout_influence['myInfluenceesCount'], 'insertion_date':datetime.datetime.now()}