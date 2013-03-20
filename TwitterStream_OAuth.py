import time
import pycurl
import urllib
import json
from Twitter_OAuth_util import load_oauth

API_ENDPOINT_URL = 'https://stream.twitter.com/1.1/statuses/filter.json'
USER_AGENT = 'TwitterStream 1.0'

POST_PARAMS = {
	'include_entities': 0,	# ???
	'stall_warning': 'true',
	'track': 'iphone,ipad,ipod'
}

#SSL_CERTIFICATE = r'SSL.crt'

class TwitterStream:
	def __init__(self, auth_header, callback, timeout=False):
		self.auth_header = auth_header
		self.callback = callback
		self.conn = None
		self.buffer = ''
		self.timeout = timeout
		self.setup_connection()

	def setup_connection(self):
		""" Create persistant HTTP connection to Streaming API endpoint using cURL.
		"""
		if self.conn:
			self.conn.close()
			self.buffer = ''
		
		self.conn = pycurl.Curl()
		
		if isinstance(self.timeout, int):	# Restart connection if less than 1 byte/s is received during "timeout" seconds
			self.conn.setopt(pycurl.LOW_SPEED_LIMIT, 1)
			self.conn.setopt(pycurl.LOW_SPEED_TIME, self.timeout)
		self.conn.setopt(pycurl.URL, API_ENDPOINT_URL)
		self.conn.setopt(pycurl.USERAGENT, USER_AGENT)
		
		self.conn.setopt(pycurl.ENCODING, 'deflate, gzip')	# Using gzip is optional but saves us bandwidth.
		self.conn.setopt(pycurl.POST, 1)
		self.conn.setopt(pycurl.POSTFIELDS, urllib.urlencode(POST_PARAMS))
		
		#self.conn.setopt(pycurl.USERPWD, "%s:%s" % (username, password))
		
		#self.conn.setopt(pycurl.CAINFO, SSL_CERTIFICATE)	# SSL_CERTIFCATE should point to the .crt file location!
		self.conn.setopt(pycurl.SSL_VERIFYPEER, 0)	# bypasses SSL certification file, 
		self.conn.setopt(pycurl.SSL_VERIFYHOST, 0)	# vulernable to "man-in-the-middle" attacks!

		self.conn.setopt(pycurl.HTTPHEADER, ['Host: stream.twitter.com', 'Authorization: %s' % self.auth_header])
		
		self.conn.setopt(pycurl.WRITEFUNCTION, self.callback)

	def get_oauth_header(self):
		""" Create and return OAuth header.
		"""
		params = {
			'oauth_version': '1.0',
			'oauth_nonce': oauth.generate_nonce(),
			'oauth_timestamp': int(time.time())
		}
		
		req = oauth.Request(method='POST', parameters=params, url='%s?%s' % (API_ENDPOINT_URL, urllib.urlencode(POST_PARAMS)))
		req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self.oauth_consumer, self.oauth_token)
		
		return req.to_header()['Authorization'].encode('utf-8')

	def start(self):
		""" Start listening to Streaming endpoint.
		Handle exceptions according to Twitter's recommendations.
		"""
		backoff_network_error = 0.25
		backoff_http_error = 5
		backoff_rate_limit = 60
		while True:
			self.setup_connection()
			try:
				self.conn.perform()
			except:
				# Network error, use linear back off up to 16 seconds
				print 'Network error: %s' % self.conn.errstr()
				print 'Waiting %s seconds before trying again' % backoff_network_error
				time.sleep(backoff_network_error)
				backoff_network_error = min(backoff_network_error + 1, 16)
				continue
			# HTTP Error
			sc = self.conn.getinfo(pycurl.HTTP_CODE)
			if sc == 420:
				# Rate limit, use exponential back off starting with 1 minute and double each attempt
				print 'Rate limit, waiting %s seconds' % backoff_rate_limit
				time.sleep(backoff_rate_limit)
				backoff_rate_limit *= 2
			else:
				# HTTP error, use exponential back off up to 320 seconds
				print 'HTTP error %s, %s' % (sc, self.conn.errstr())
				print 'Waiting %s seconds' % backoff_http_error
				time.sleep(backoff_http_error)
				backoff_http_error = min(backoff_http_error * 2, 320)

	def handle_tweet(self, data):
		""" This method is called when data is received through Streaming endpoint.
		"""
		self.buffer += data
		if data.endswith('\r\n') and self.buffer.strip():
			# complete message received
			message = json.loads(self.buffer)
			self.buffer = ''
			msg = ''
			if message.get('limit'):
				print 'Rate limiting caused us to miss %s tweets' % (message['limit'].get('track'))
			elif message.get('disconnect'):
				raise Exception('Got disconnect: %s' % message['disconnect'].get('reason'))
			elif message.get('warning'):
				print 'Got warning: %s' % message['warning'].get('message')
			else:
				print 'Got tweet with text: %s' % message.get('text')

def hose(data):
	print data

def filter_stream(consumer_key, consumer_secret, queries, callback=hose):
	POST_PARAMS['track'] = ','.join(query for query in queries)

	auth_header = load_oauth(consumer_key, consumer_secret, POST_PARAMS)

	ts = TwitterStream(auth_header, callback)
	ts.setup_connection()
	ts.start()

def test(consumer_key, consumer_secret, queries=['google']):
	OAUTH_KEYS = {
		'consumer_key': consumer_key,
		'consumer_secret': consumer_secret,
	}

	filter_stream(OAUTH_KEYS['consumer_key'], OAUTH_KEYS['consumer_secret'], queries=queries)

if __name__ == '__main__':
	pass