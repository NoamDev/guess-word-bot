import os
import tweepy
from flask import Flask, request

os.environ['TWITTER_CONSUMER_KEY']
oauth1_user_handler = tweepy.OAuthHandler(
    os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'],
    callback="http://localhost:12241"
)
print(oauth1_user_handler.get_authorization_url())
app = Flask(__name__)
@app.route('/')
def auth():
    oauth_token = request.args['oauth_token']
    oauth_verifier = request.args['oauth_verifier']

    access_token, access_token_secret = oauth1_user_handler.get_access_token(verifier=oauth_verifier)
    access_token
    access_token_secret
    print(f'Authentication complete, access token: {access_token}, access_token_secret: {access_token_secret}')
    return 'Success!'

app.run(host="localhost", port=12241)