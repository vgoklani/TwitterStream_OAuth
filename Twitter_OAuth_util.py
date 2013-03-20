import oauth2 as oauth
import urlparse
import webbrowser
import urllib
import time

ACCESS_TOKEN_FILE = 'TWITTER_OAUTH_ACCESS_TOKEN'

TWITTER_REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
TWITTER_ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'
TWITTER_AUTHORIZE_URL = 'https://twitter.com/oauth/authorize'

TWITTER_STREAM_API_HOST = 'stream.twitter.com'
TWITTER_STREAM_API_PATH = '/1.1/statuses/filter.json'

CONSUMER = None

def save_access_token(key, secret):
	with open(ACCESS_TOKEN_FILE, 'w') as f:
		f.write("ACCESS_KEY=%s\n" % key)
		f.write("ACCESS_SECRET=%s\n" % secret)

def load_access_token():
	with open(ACCESS_TOKEN_FILE) as f:
		lines = f.readlines()

	str_key = lines[0].strip().split('=')[1]
	str_secret = lines[1].strip().split('=')[1]
	return oauth.Token(key=str_key, secret=str_secret)

def fetch_access_token():
	client = oauth.Client(CONSUMER)

	# Step 1: Get a request token.
	resp, content = client.request(TWITTER_REQUEST_TOKEN_URL, "GET")
	if resp['status'] != '200':
		raise Exception("Invalid response %s." % resp['status'])
	request_token = dict(urlparse.parse_qsl(content))
	print "Request Token:"
	print "     oauth_token        = %s" % request_token['oauth_token']
	print "     oauth_token_secret = %s" % request_token['oauth_token_secret']

	# Step 2: User must authorize application.
	auth_url = "%s?oauth_token=%s" % (TWITTER_AUTHORIZE_URL, request_token['oauth_token'])
	webbrowser.open_new_tab(auth_url)
	print "Go to the following link in your browser:"
	print auth_url
	pin = raw_input('What is the PIN? ')
	token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
	token.set_verifier(pin)

	# Step 3: Get access token.
	client = oauth.Client(CONSUMER, token)
	resp, content = client.request(TWITTER_ACCESS_TOKEN_URL, "POST")
	if resp['status'] != '200':
		raise Exception("Invalid response %s." % resp['status'])
	access_token = dict(urlparse.parse_qsl(content))
	print "Access Token:"
	print "     oauth_token        = %s" % request_token['oauth_token']
	print "     oauth_token_secret = %s" % request_token['oauth_token_secret']
	return (access_token['oauth_token'], access_token['oauth_token_secret'])

def get_oauth_header(access_token):
	url = "https://%s%s" % (TWITTER_STREAM_API_HOST, TWITTER_STREAM_API_PATH)
	params = {
		'oauth_version': "1.0",
		'oauth_nonce': oauth.generate_nonce(),
		'oauth_timestamp': int(time.time()),
		'oauth_token': access_token.key,	# ???
		'oauth_consumer_key': CONSUMER.key	# ???
	}

	# For some messed up reason, we need to specify is_form_encoded to prevent the oauth2 library from setting oauth_body_hash which Twitter doesn't like.
	req = oauth.Request(method="GET", url=url, parameters=params)#, is_form_encoded=True)
	req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), CONSUMER, access_token)
	return req.to_header()['Authorization'].encode('utf-8')

def get_oauth_header_POST(access_token, POST_PARAMS):
	url = "https://%s%s?%s" % (TWITTER_STREAM_API_HOST, TWITTER_STREAM_API_PATH, urllib.urlencode(POST_PARAMS))
	params = {
		'oauth_version': '1.0',
		'oauth_nonce': oauth.generate_nonce(),
		'oauth_timestamp': int(time.time())
	}
	req = oauth.Request(method='POST', url=url, parameters=params)
	req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), CONSUMER, access_token)
	return req.to_header()['Authorization'].encode('utf-8')

def load_oauth(CONSUMER_KEY, CONSUMER_SECRET, POST_PARAMS):
	global CONSUMER
	CONSUMER = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)

	# Check if we have saved an access token before.
	try:
		f = open(ACCESS_TOKEN_FILE)
	except IOError:
		# No saved access token. Do the 3-legged OAuth dance and fetch one.
		(access_token_key, access_token_secret) = fetch_access_token()
		# Save the access token for next time.
		save_access_token(access_token_key, access_token_secret)

	# Load access token from disk.
	access_token = load_access_token()

	# Build Authorization header from the access_token.
	auth_header = get_oauth_header_POST(access_token, POST_PARAMS)

	return auth_header

def test(consumer_key, consumer_secret):
	OAUTH_KEYS = {
		'consumer_key': consumer_key,
		'consumer_secret': consumer_secret,
	}

	POST_PARAMS = {
		'include_entities': 0,
		'stall_warning': 'true',
		'track': 'iphone,ipad,ipod'
	}

	auth_header = load_oauth(OAUTH_KEYS['consumer_key'], OAUTH_KEYS['consumer_secret'], POST_PARAMS)