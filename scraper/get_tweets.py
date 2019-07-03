'''
collects tweets using the twitter API.
'''
import tweepy
from api import get_api_handler


def get_tweets_for_hastag(tag):
    '''
    get tweets for a particular hashtag
    '''
    api = get_api_handler()
    tweets = tweepy.Cursor(api.search, q='#{}'.format(tag),
                           rpp=100, languages=['en']).items()

    return tweets
