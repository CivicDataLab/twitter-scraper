'''
collects tweets using the twitter API.
'''
import sys
import tweepy

from api import get_api_handler


def get_tweets_for_hastag(tag):
    '''
    get tweets for a particular hashtag
    '''
    api = get_api_handler()
    budget_tweets = tweepy.Cursor(api.search, q='#{}'.format(tag),
                                  rpp=100, languages=['en']).items()
    for tweet in budget_tweets:
        print(tweet.text.encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide the hashtag to search for')
        sys.exit()
    HASTAG = sys.argv[1]
    get_tweets_for_hastag(HASTAG)
