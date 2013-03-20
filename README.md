Quick code snippet for accessing the *filtered* Twitter Streaming API with OAuth authentication.

First: get a consumer key/secret from dev.twitter.com

Second: just call the filter_stream() in TwitterStream_OAuth.py, passing in your consumer key/secret from above, 
and a comma separated list of keywords (i.e. ['iphone','ipad','ipod']).

The OAuth dance will open your default browser, and generate an access key/secret to authorize the streaming client. This will
then get saved in *clear* text in your local directory (you might want to encrypt it).

Also note that I had issues assigning the SSL certificate to pycurl, so this version ignores the SSL check!
You've been warned!

The default callback function will output all tweets to stdout. You should define your own callback, and pipe the data to
(say) MongoDB, etc.

There are also two files that handle access to Klout and Peerindex. Just get api_key(s) and you're all set!