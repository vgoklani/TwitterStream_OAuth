## Access the *filtered* Twitter Streaming API via OAuth authentication

* first get a consumer key/secret from dev.twitter.com

* then just call filter_stream() from TwitterStream_OAuth.py, passing in your consumer key/secret from above, 
and a comma separated list of keywords (i.e. ['iphone','ipad','ipod']).

During the first run, the OAuth dance will open your default browser and generate an access key/secret to authorize the streaming client.
The access key/secret will then get saved locally, as a *clear* text file. (you might want to encrypt it).

Also note that I had issues assigning the SSL certificate to pycurl, so this version ignores the SSL check!

The default callback function will output all tweets to stdout. You should define your own callback, and pipe the data to
(say) MongoDB, etc.

There are also two files that handle access to Klout and Peerindex. Just get api_key(s) and you're all set!
