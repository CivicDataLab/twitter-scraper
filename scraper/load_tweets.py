# pylint: disable=invalid-name
'''
fetch and loads tweets into db.
'''
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from get_tweets import get_tweets_for_hastag
from models import TweetData


def save_tweets(tweets):
    '''
    save tweets to db.
    '''
    engine = create_engine('sqlite:///twitter_db', echo=True)
    session = sessionmaker()
    session.configure(bind=engine)
    session = session()

    for tweet in tweets:
        tweet_json = TweetData(tweet._json)
        session.add(tweet_json)
        print(tweet.text.encode('utf-8'))
        session.commit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please provide the hashtag to search for')
        sys.exit()
    HASTAG = sys.argv[1]
    hashtag_tweets = get_tweets_for_hastag(HASTAG)
    save_tweets(hashtag_tweets)
