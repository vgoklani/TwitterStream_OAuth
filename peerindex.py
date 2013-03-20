# https://developers.peerindex.com/docs/
import requests, urllib
import datetime

def get_peerindex_actor(twitter_screen_name, method, api_key):
	assert method in ('basic', 'extended', 'topic', 'graph')
	
	parameters = {
		'twitter_screen_name' : twitter_screen_name,
		'api_key' : api_key
	}

	r = requests.get( 'https://api.peerindex.com/1/actor/%s?%s' % (method, urllib.urlencode(parameters)) )
	
	return r.json()