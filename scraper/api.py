'''
Setup authorization for the API.
'''
import tweepy

from settings import ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET

def get_api_handler():
    '''
    configure the credentials and returns an object for accessing the API.
    '''
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api
